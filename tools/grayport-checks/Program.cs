using System.Text.Json;
using ShadowOfTheUniverse.V2.Core;

string root = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../../"));
string layout = Path.Combine(root, "UnityProjectV2/Assets/_ProjectV2/Generated/Levels/Grayport/grayport-layout.json");
using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(layout));
var checks = new List<string>();
void Check(bool value, string name) { if (!value) throw new Exception(name); checks.Add(name); }
MissionState Create()
{
    var s = new MissionState { MissionId = "grayport_blackout", TargetNodeId = "relay", ExtractionNodeId = "extract", TimeLimitSeconds = 300, MaxAlertLevel = 5, ObjectiveRequired = 3 };
    foreach(var n in doc.RootElement.GetProperty("nodes").EnumerateArray())
    {
        var p = n.GetProperty("position").EnumerateArray().Select(x=>x.GetSingle()).ToArray();
        s.Map.AddNode(new NodeDefinition { Id=n.GetProperty("id").GetString(), DisplayName=n.GetProperty("label").GetString(), X=p[0], Elevation=p[1], Y=p[2], Terrain=TerrainType.Coastal,
            Exposure=n.GetProperty("exposure").GetInt32(), CoverRating=n.GetProperty("cover").GetInt32(), PoweredGuard=n.GetProperty("poweredGuard").GetBoolean(), Interaction=(NodeInteraction)n.GetProperty("interaction").GetInt32() });
    }
    foreach(var r in doc.RootElement.GetProperty("routes").EnumerateArray())
        s.Map.AddRoute(new RouteDefinition {FromNodeId=r.GetProperty("a").GetString(), ToNodeId=r.GetProperty("b").GetString(), RouteType=RouteType.LandRoute});
    foreach(var p in doc.RootElement.GetProperty("patrols").EnumerateArray())
        s.Patrols.Add(new PatrolDefinition { Id=p.GetProperty("id").GetString(), Nodes=p.GetProperty("nodes").EnumerateArray().Select(n=>n.GetString()).ToArray(), SecondsPerLeg=p.GetProperty("secondsPerLeg").GetInt32(), PhaseOffsetSeconds=p.GetProperty("offset").GetInt32(), ExtractionOnly=p.GetProperty("extractionOnly").GetBoolean() });
    s.Encounters.Enabled=true;
    s.Units.Add(new UnitState { Id="echo", DisplayName="Echo", CurrentNodeId="entry", Domain=UnitDomain.Land, Scale=UnitScale.Individual, CurrentHealth=100, MaxHealth=100, CompromisePoints=100 });
    return s;
}
string[][] paths = {
    new[]{"fork","gate","checkpoint","ramp","relay_front","relay"},
    new[]{"fork","containers","warehouse","intel","backgate","relay_west","relay"},
    new[]{"shore","coast","maintenance","power","rear","backgate","relay_west","relay"}
};
var skill=new SkillData { Id="heat", DisplayName="Heat", BaseSuccessRate=90, ObjectiveProgressOnSuccess=1, RealityDebtCost=8, FatigueCost=8, AlertOnFailure=1, BacklashDamage=10, CompromiseCost=10 };
var routeCosts = new List<object>();
for(int i=0;i<paths.Length;i++)
{
    var s=Create();
    foreach(string id in paths[i])
    {
        string before=s.Units[0].CurrentNodeId;
        Check(MissionResolver.ValidateMove(s,"echo",id).Success,$"route_{i}_{id}_valid");
        Check(s.Units[0].CurrentNodeId==before,$"route_{i}_{id}_validation_no_mutation");
        Check(MissionResolver.MoveUnit(s,"echo",id).Success,$"route_{i}_{id}_arrival");
    }
    for(int j=0;j<3;j++) MissionResolver.ApplySkillResolution(s,s.Units[0],RiskResolver.Resolve(s.Units[0],skill,1));
    Check(s.Outcome==MissionOutcome.Running,$"route_{i}_objective_requires_extraction");
    foreach(string id in new[]{"relay_east","dock","extract"}) Check(MissionResolver.MoveUnit(s,"echo",id).Success,$"route_{i}_exit_{id}");
    Check(s.Outcome==MissionOutcome.Victory,$"route_{i}_victory");
    routeCosts.Add(new { route=i, alert=s.AlertLevel, budget=s.Units[0].CompromisePoints });
    Check(!MissionResolver.MoveUnit(s,"echo","dock").Success,$"route_{i}_terminal_locked");
}
{
    var s=Create(); var gate=s.Map.GetNode("gate");
    Check(TacticalEncounterResolver.ArrivalAlert(s,gate,0)==2,"guard_plus_patrol_exposure");
    Check(TacticalEncounterResolver.ArrivalAlert(s,gate,12)==1,"patrol_window_reduces_exposure");
    Check(TacticalEncounterResolver.ArrivalAlert(s,s.Map.GetNode("containers"),0)==0,"cover_screens_yard_patrol");
    var checkpoint=s.Map.GetNode("checkpoint");
    Check(TacticalEncounterResolver.ArrivalAlert(s,checkpoint,0)==1,"powered_guard_before_switch");
    s.Units[0].CurrentNodeId="power";
    Check(TacticalEncounterResolver.Interact(s,"echo").Success,"power_switch_works");
    Check(s.Encounters.PowerDisabled && s.Units[0].CompromisePoints==90 && s.ElapsedSeconds==8,"power_cost_and_state");
    Check(TacticalEncounterResolver.ArrivalAlert(s,checkpoint,0)==0,"power_suppresses_fixed_guard");
    Check(!TacticalEncounterResolver.Interact(s,"echo").Success && s.Units[0].CompromisePoints==90,"power_not_repeatable");
    s.Units[0].CurrentNodeId="intel";
    Check(TacticalEncounterResolver.Interact(s,"echo").Success && s.Encounters.ReconDownloaded,"recon_unlocks_patrol_information");
    Check(s.ElapsedSeconds==16,"interaction_time_costs_recorded");
    Check(!TacticalEncounterResolver.Interact(s,"echo").Success,"recon_not_repeatable");
}
{
    var s=Create(); var response=s.Patrols.Single(p=>p.ExtractionOnly);
    Check(TacticalEncounterResolver.PatrolNodeAt(s,response,0)==null,"response_not_active_during_approach");
    s.ObjectiveProgress=s.ObjectiveRequired;
    TacticalEncounterResolver.UpdatePhase(s);
    Check(s.Encounters.Phase==TacticalPhase.ExtractionWarning,"objective_warns_before_pressure");
    MissionResolver.AdvanceTime(s,7);
    Check(TacticalEncounterResolver.PatrolNodeAt(s,response,s.ElapsedSeconds)==null,"response_waits_for_warning");
    MissionResolver.AdvanceTime(s,1);
    Check(s.Encounters.Phase==TacticalPhase.Extraction,"response_activates_after_warning");
    Check(TacticalEncounterResolver.PatrolNodeAt(s,response,s.ElapsedSeconds)!=null,"response_has_waypoint");
    Check(s.Map.TryGetRoute("dock","extract",out var route),"extraction_route_stays_open");
}
{
    var s=Create(); var u=s.Units[0]; u.CompromisePoints=9;
    int hp=u.CurrentHealth;
    var denied=RiskResolver.Resolve(u,skill,1);
    Check(!denied.Assessment.CanUse && u.CompromisePoints==9 && u.CurrentHealth==hp && u.RealityDebt==0,"budget_denial_has_no_mutation");
    u.CompromisePoints=10;
    var success=RiskResolver.Resolve(u,skill,1);
    Check(success.Success && success.CompromiseSpent==10 && u.CompromisePoints==0,"success_consumes_budget");
    u.CompromisePoints=10;
    var failure=RiskResolver.Resolve(u,skill,100);
    Check(!failure.Success && failure.CompromiseSpent==10 && u.CompromisePoints==0,"failure_consumes_budget");
    u.CurrentNodeId="power";
    Check(!TacticalEncounterResolver.Interact(s,"echo").Success && !s.Encounters.PowerDisabled,"power_denied_without_budget");
}
{
    var s=Create(); s.Outcome=MissionOutcome.Failed; s.Units[0].CurrentNodeId="intel";
    Check(!TacticalEncounterResolver.Interact(s,"echo").Success && !s.Encounters.ReconDownloaded,"terminal_interaction_locked");
    var fresh=Create();
    Check(!fresh.Encounters.ReconDownloaded && !fresh.Encounters.PowerDisabled && fresh.Encounters.Phase==TacticalPhase.Approach,"new_state_has_no_encounter_leak");
}
{
    var s=Create(); s.Units[0].CurrentHealth=0;
    Check(!MissionResolver.MoveUnit(s,"echo","fork").Success,"dead_unit_move_rejected");
    Check(s.Units[0].CurrentNodeId=="entry","dead_unit_position_unchanged");
    MissionResolver.CheckOutcome(s); Check(s.Outcome==MissionOutcome.Failed,"all_dead_failure");
}
{
    var s=Create(); Check(!MissionResolver.MoveUnit(s,"echo","relay").Success,"skip_route_rejected");
    MissionResolver.AdvanceTime(s,300); Check(s.Outcome==MissionOutcome.Failed,"timeout_failure");
}
{
    var s=Create(); s.AlertLevel=5; MissionResolver.CheckOutcome(s); Check(s.Outcome==MissionOutcome.Failed,"alert_failure");
}
{
    var s=Create(); s.Units[0].CurrentNodeId="extract"; MissionResolver.CheckOutcome(s);
    Check(s.Outcome==MissionOutcome.Running,"early_extraction_not_victory");
    MissionResolver.ApplySkillResolution(s,s.Units[0],RiskResolver.Resolve(s.Units[0],skill,1));
    Check(s.ObjectiveProgress==0,"off_target_skill_no_progress");
}
{
    var s=Create(); var u=s.Units[0];
    var result=RiskResolver.Resolve(u,skill,100);
    Check(!result.Success && u.CurrentHealth==90 && u.RealityDebt==12,"forced_failure_costs");
    u.Cooldowns[skill.Id]=1;
    Check(!RiskResolver.Assess(u,skill).CanUse,"cooldown_blocks_skill");
}
var output=new { status="passed", checks=checks.Count, route_completions=3, route_costs=routeCosts, runtime="dotnet / actual Core sources", unity_play_mode="not_run", names=checks };
string json=JsonSerializer.Serialize(output,new JsonSerializerOptions{WriteIndented=true});
File.WriteAllText(Path.Combine(root,"docs/grayport/core-checks.json"),json+"\n");
Console.WriteLine($"PASS: {checks.Count} checks, 3 authored routes completed using actual Core rules.");
