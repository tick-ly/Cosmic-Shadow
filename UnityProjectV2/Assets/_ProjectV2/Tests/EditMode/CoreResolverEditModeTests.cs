using NUnit.Framework;
using ShadowOfTheUniverse.V2.Core;

namespace ShadowOfTheUniverse.V2.Tests.EditMode
{
    public sealed class CoreResolverEditModeTests
    {
        [Test]
        public void SkillSuccessRateDropsWithDebtFatigueAndRepeatedUse()
        {
            UnitState unit = CreateUnit();
            SkillData skill = CreateSkill(90);

            SkillRiskAssessment clean = RiskResolver.Assess(unit, skill);

            unit.RealityDebt = 850;
            unit.Fatigue = 80;
            unit.ConsecutiveUses[skill.Id] = 2;

            SkillRiskAssessment stressed = RiskResolver.Assess(unit, skill);

            Assert.That(clean.SuccessRate, Is.EqualTo(95));
            Assert.That(stressed.SuccessRate, Is.LessThan(clean.SuccessRate));
        }

        [Test]
        public void FailedSkillAddsDebtFatigueAlertAndBacklash()
        {
            UnitState unit = CreateUnit();
            SkillData skill = CreateSkill(60);

            SkillResolution result = RiskResolver.Resolve(unit, skill, 99);

            Assert.That(result.Success, Is.False);
            Assert.That(unit.RealityDebt, Is.EqualTo(15));
            Assert.That(unit.Fatigue, Is.EqualTo(20));
            Assert.That(unit.CurrentHealth, Is.EqualTo(88));
            Assert.That(result.AlertAdded, Is.EqualTo(1));
        }

        [Test]
        public void MissionVictoryRequiresObjectiveAndExtraction()
        {
            MissionState mission = new MissionState
            {
                ObjectiveRequired = 3,
                ObjectiveProgress = 3,
                ExtractionNodeId = "extract",
                TimeLimitSeconds = 300,
                MaxAlertLevel = 3
            };

            mission.Units.Add(new UnitState
            {
                Id = "operator",
                DisplayName = "Operator",
                CurrentNodeId = "target",
                MaxHealth = 100,
                CurrentHealth = 100
            });

            MissionResolver.CheckOutcome(mission);
            Assert.That(mission.Outcome, Is.EqualTo(MissionOutcome.Running));

            mission.Units[0].CurrentNodeId = "extract";
            MissionResolver.CheckOutcome(mission);

            Assert.That(mission.Outcome, Is.EqualTo(MissionOutcome.Victory));
        }

        [Test]
        public void MoveFailsWhenNodesAreNotConnected()
        {
            MissionState mission = CreateMovementMission();

            MoveResult result = MissionResolver.MoveUnit(mission, "operator", "isolated");

            Assert.That(result.Success, Is.False);
            Assert.That(result.Reason, Is.EqualTo("Nodes are not connected."));
            Assert.That(mission.GetUnit("operator").CurrentNodeId, Is.EqualTo("base"));
        }

        [Test]
        public void MoveFailsWhenTerrainIsIncompatible()
        {
            MissionState mission = CreateMovementMission();

            MoveResult result = MissionResolver.MoveUnit(mission, "operator", "sea");

            Assert.That(result.Success, Is.False);
            Assert.That(result.Reason, Is.EqualTo("Unit cannot enter this terrain."));
            Assert.That(mission.GetUnit("operator").CurrentNodeId, Is.EqualTo("base"));
        }

        [Test]
        public void SkillCannotResolveWhileCoolingDown()
        {
            UnitState unit = CreateUnit();
            SkillData skill = CreateSkill(80);
            unit.Cooldowns[skill.Id] = 1;

            SkillResolution result = RiskResolver.Resolve(unit, skill, 1);

            Assert.That(result.Success, Is.False);
            Assert.That(result.Summary, Is.EqualTo("Skill is cooling down."));
            Assert.That(unit.RealityDebt, Is.EqualTo(0));
        }

        [Test]
        public void AlertThresholdFailsMission()
        {
            MissionState mission = new MissionState
            {
                TimeLimitSeconds = 300,
                MaxAlertLevel = 3,
                AlertLevel = 2,
                ObjectiveRequired = 3
            };
            UnitState unit = CreateUnit();
            mission.Units.Add(unit);
            SkillData skill = CreateSkill(20);

            SkillResolution result = RiskResolver.Resolve(unit, skill, 99);
            MissionResolver.ApplySkillResolution(mission, unit, result);

            Assert.That(mission.AlertLevel, Is.EqualTo(3));
            Assert.That(mission.Outcome, Is.EqualTo(MissionOutcome.Failed));
        }

        [Test]
        public void TimeLimitFailsMission()
        {
            MissionState mission = new MissionState
            {
                TimeLimitSeconds = 60,
                MaxAlertLevel = 3,
                ObjectiveRequired = 3
            };
            mission.Units.Add(CreateUnit());

            MissionResolver.AdvanceTime(mission, 60);

            Assert.That(mission.Outcome, Is.EqualTo(MissionOutcome.Failed));
        }

        private static UnitState CreateUnit()
        {
            return new UnitState
            {
                Id = "operator",
                DisplayName = "Operator",
                Domain = UnitDomain.Land,
                Scale = UnitScale.Individual,
                CurrentNodeId = "base",
                MaxHealth = 100,
                CurrentHealth = 100
            };
        }

        private static SkillData CreateSkill(int baseSuccessRate)
        {
            return new SkillData
            {
                Id = "heat_shift",
                DisplayName = "Heat Shift",
                BaseSuccessRate = baseSuccessRate,
                RealityDebtCost = 10,
                BacklashDamage = 12,
                FatigueCost = 10,
                AlertOnFailure = 1,
                ObjectiveProgressOnSuccess = 1,
                SuccessDescription = "Success",
                FailureDescription = "Failure"
            };
        }

        private static MissionState CreateMovementMission()
        {
            MissionState mission = new MissionState
            {
                TimeLimitSeconds = 300,
                MaxAlertLevel = 3,
                ObjectiveRequired = 3
            };

            mission.Map.AddNode(new NodeDefinition { Id = "base", DisplayName = "Base", Terrain = TerrainType.Land });
            mission.Map.AddNode(new NodeDefinition { Id = "ridge", DisplayName = "Ridge", Terrain = TerrainType.Land });
            mission.Map.AddNode(new NodeDefinition { Id = "sea", DisplayName = "Sea", Terrain = TerrainType.Sea });
            mission.Map.AddNode(new NodeDefinition { Id = "isolated", DisplayName = "Isolated", Terrain = TerrainType.Land });
            mission.Map.AddRoute(new RouteDefinition { FromNodeId = "base", ToNodeId = "ridge", RouteType = RouteType.LandRoute });
            mission.Map.AddRoute(new RouteDefinition { FromNodeId = "base", ToNodeId = "sea", RouteType = RouteType.LandRoute });

            UnitState unit = CreateUnit();
            unit.Scale = UnitScale.Squad;
            mission.Units.Add(unit);
            return mission;
        }
    }
}
