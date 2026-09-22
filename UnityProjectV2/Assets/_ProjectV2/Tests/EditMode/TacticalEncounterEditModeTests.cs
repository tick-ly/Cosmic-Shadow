using NUnit.Framework;
using ShadowOfTheUniverse.V2.Core;

namespace ShadowOfTheUniverse.V2.Tests
{
    public sealed class TacticalEncounterEditModeTests
    {
        private static MissionState Mission()
        {
            var s = new MissionState { TimeLimitSeconds=300, MaxAlertLevel=5, ObjectiveRequired=3, TargetNodeId="target", ExtractionNodeId="extract" };
            s.Encounters.Enabled = true;
            s.Map.AddNode(new NodeDefinition { Id="base" });
            s.Map.AddNode(new NodeDefinition { Id="guard", Exposure=1, PoweredGuard=true });
            s.Map.AddNode(new NodeDefinition { Id="covered", CoverRating=1 });
            s.Map.AddNode(new NodeDefinition { Id="intel", Interaction=NodeInteraction.ReconTerminal });
            s.Map.AddNode(new NodeDefinition { Id="power", Interaction=NodeInteraction.PowerSwitch });
            s.Map.AddNode(new NodeDefinition { Id="target" });
            s.Map.AddNode(new NodeDefinition { Id="extract" });
            s.Map.AddRoute(new RouteDefinition { FromNodeId="base", ToNodeId="guard", RouteType=RouteType.LandRoute });
            s.Patrols.Add(new PatrolDefinition { Id="watch", Nodes=new[] { "guard", "covered" }, SecondsPerLeg=10 });
            s.Patrols.Add(new PatrolDefinition { Id="response", Nodes=new[] { "extract", "target" }, SecondsPerLeg=10, ExtractionOnly=true });
            s.Units.Add(new UnitState { Id="unit", CurrentNodeId="base", Domain=UnitDomain.Land, Scale=UnitScale.Individual, MaxHealth=100, CurrentHealth=100, CompromisePoints=100 });
            return s;
        }

        [Test]
        public void PatrolWindowAndCoverModifyArrivalExposure()
        {
            var s=Mission();
            Assert.That(TacticalEncounterResolver.ArrivalAlert(s,s.Map.GetNode("guard"),0),Is.EqualTo(2));
            Assert.That(TacticalEncounterResolver.ArrivalAlert(s,s.Map.GetNode("guard"),10),Is.EqualTo(1));
            Assert.That(TacticalEncounterResolver.ArrivalAlert(s,s.Map.GetNode("covered"),10),Is.Zero);
        }

        [Test]
        public void ReconCostsTimeAndRunsOnce()
        {
            var s=Mission(); s.Units[0].CurrentNodeId="intel";
            Assert.That(TacticalEncounterResolver.Interact(s,"unit").Success,Is.True);
            Assert.That(s.Encounters.ReconDownloaded,Is.True);
            Assert.That(s.ElapsedSeconds,Is.EqualTo(8));
            Assert.That(TacticalEncounterResolver.Interact(s,"unit").Success,Is.False);
            Assert.That(s.ElapsedSeconds,Is.EqualTo(8));
        }

        [Test]
        public void PowerConsumesBudgetAndSuppressesGuardNotPatrol()
        {
            var s=Mission(); s.Units[0].CurrentNodeId="power";
            Assert.That(TacticalEncounterResolver.Interact(s,"unit").Success,Is.True);
            Assert.That(s.Units[0].CompromisePoints,Is.EqualTo(90));
            Assert.That(TacticalEncounterResolver.ArrivalAlert(s,s.Map.GetNode("guard"),0),Is.EqualTo(1));
            Assert.That(TacticalEncounterResolver.ArrivalAlert(s,s.Map.GetNode("guard"),10),Is.Zero);
        }

        [Test]
        public void InsufficientBudgetHasNoSideEffects()
        {
            var s=Mission(); var u=s.Units[0]; u.CompromisePoints=9;
            var skill=new SkillData { Id="skill", CompromiseCost=10, BaseSuccessRate=90 };
            Assert.That(RiskResolver.Resolve(u,skill,1).Assessment.CanUse,Is.False);
            Assert.That(u.CompromisePoints,Is.EqualTo(9));
            Assert.That(u.RealityDebt,Is.Zero);
            u.CurrentNodeId="power";
            Assert.That(TacticalEncounterResolver.Interact(s,"unit").Success,Is.False);
            Assert.That(s.ElapsedSeconds,Is.Zero);
            Assert.That(s.Encounters.PowerDisabled,Is.False);
        }

        [Test]
        public void ExtractionPatrolHasEightSecondWarning()
        {
            var s=Mission(); s.ObjectiveProgress=3;
            TacticalEncounterResolver.UpdatePhase(s);
            Assert.That(s.Encounters.Phase,Is.EqualTo(TacticalPhase.ExtractionWarning));
            MissionResolver.AdvanceTime(s,7);
            Assert.That(TacticalEncounterResolver.PatrolActive(s,s.Patrols[1]),Is.False);
            MissionResolver.AdvanceTime(s,1);
            Assert.That(TacticalEncounterResolver.PatrolActive(s,s.Patrols[1]),Is.True);
            Assert.That(s.Encounters.Phase,Is.EqualTo(TacticalPhase.Extraction));
        }

        [Test]
        public void DownedUnitAndFinishedMissionRejectActions()
        {
            var s=Mission(); s.Units[0].CurrentHealth=0;
            Assert.That(MissionResolver.MoveUnit(s,"unit","guard").Success,Is.False);
            s.Units[0].CurrentHealth=100; s.Units[0].CurrentNodeId="intel"; s.Outcome=MissionOutcome.Failed;
            Assert.That(TacticalEncounterResolver.Interact(s,"unit").Success,Is.False);
            Assert.That(s.Encounters.ReconDownloaded,Is.False);
        }

        [Test]
        public void ValidationDoesNotMoveOrTriggerDetection()
        {
            var s=Mission();
            Assert.That(MissionResolver.ValidateMove(s,"unit","guard").Success,Is.True);
            Assert.That(s.Units[0].CurrentNodeId,Is.EqualTo("base"));
            Assert.That(s.AlertLevel,Is.Zero);
            MissionResolver.MoveUnit(s,"unit","guard");
            Assert.That(s.AlertLevel,Is.EqualTo(2));
        }

        [Test]
        public void NewMissionDoesNotShareInteractionState()
        {
            var first=Mission(); first.Units[0].CurrentNodeId="intel";
            TacticalEncounterResolver.Interact(first,"unit");
            var second=Mission();
            Assert.That(second.Encounters.ReconDownloaded,Is.False);
            Assert.That(second.Encounters.UsedInteractions.Count,Is.Zero);
        }
    }
}
