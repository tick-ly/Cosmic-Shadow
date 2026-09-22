using System;

namespace ShadowOfTheUniverse.V2.Core
{
    public sealed class SkillRiskAssessment
    {
        public SkillData Skill;
        public int SuccessRate;
        public SkillRiskLevel RiskLevel;
        public bool CanUse;
        public string Reason;
    }

    public sealed class SkillResolution
    {
        public SkillRiskAssessment Assessment;
        public int Roll;
        public bool Success;
        public int DebtAdded;
        public int FatigueAdded;
        public int BacklashDamage;
        public int ObjectiveProgressAdded;
        public int AlertAdded;
        public int CompromiseSpent;
        public string Summary;
    }

    public static class RiskResolver
    {
        public static SkillRiskAssessment Assess(UnitState user, SkillData skill)
        {
            if (user == null || skill == null)
            {
                return new SkillRiskAssessment { Skill = skill, CanUse = false, Reason = "Missing unit or skill." };
            }

            int cooldown = user.GetCooldown(skill.Id);
            if (cooldown > 0)
            {
                return new SkillRiskAssessment { Skill = skill, CanUse = false, Reason = "Skill is cooling down." };
            }

            if (!user.IsAlive)
            {
                return new SkillRiskAssessment { Skill = skill, CanUse = false, Reason = "Unit is down." };
            }

            if (user.CompromisePoints < Math.Max(0, skill.CompromiseCost))
            {
                return new SkillRiskAssessment { Skill = skill, CanUse = false, Reason = "Insufficient compromise points." };
            }

            int rate = skill.BaseSuccessRate;
            rate -= user.GetConsecutiveUses(skill.Id) * 5;
            rate -= user.RealityDebt >= 500 ? 10 : 0;
            rate -= user.RealityDebt >= 800 ? 10 : 0;
            rate -= user.Fatigue >= 70 ? 15 : 0;
            rate += user.Scale == UnitScale.Individual ? 5 : 0;
            rate = MissionMath.ClampInt(rate, 10, 95);

            return new SkillRiskAssessment
            {
                Skill = skill,
                SuccessRate = rate,
                RiskLevel = Classify(rate),
                CanUse = true,
                Reason = "Ready"
            };
        }

        public static SkillResolution Resolve(UnitState user, SkillData skill, int? forcedRoll = null, Random random = null)
        {
            SkillRiskAssessment assessment = Assess(user, skill);
            if (!assessment.CanUse)
            {
                return new SkillResolution
                {
                    Assessment = assessment,
                    Roll = 0,
                    Success = false,
                    Summary = assessment.Reason
                };
            }

            Random rng = random ?? new Random();
            int roll = forcedRoll.HasValue ? forcedRoll.Value : rng.Next(1, 101);
            bool success = roll <= assessment.SuccessRate;
            int debt = success ? skill.RealityDebtCost : (int)Math.Ceiling(skill.RealityDebtCost * 1.5f);
            int fatigue = success ? skill.FatigueCost : skill.FatigueCost + 10;
            int backlash = success ? 0 : skill.BacklashDamage;
            int objectiveProgress = success ? skill.ObjectiveProgressOnSuccess : 0;
            int alert = success ? 0 : Math.Max(1, skill.AlertOnFailure);
            int spent = Math.Max(0, skill.CompromiseCost);
            user.CompromisePoints -= spent;

            user.RealityDebt = MissionMath.ClampInt(user.RealityDebt + debt, 0, 2000);
            user.Fatigue = MissionMath.ClampInt(user.Fatigue + fatigue, 0, 100);
            user.CurrentHealth = MissionMath.ClampInt(user.CurrentHealth - backlash, 0, user.MaxHealth);
            user.Cooldowns[skill.Id] = Math.Max(0, skill.CooldownTurns);
            user.ConsecutiveUses[skill.Id] = user.GetConsecutiveUses(skill.Id) + 1;

            return new SkillResolution
            {
                Assessment = assessment,
                Roll = roll,
                Success = success,
                DebtAdded = debt,
                FatigueAdded = fatigue,
                BacklashDamage = backlash,
                ObjectiveProgressAdded = objectiveProgress,
                AlertAdded = alert,
                CompromiseSpent = spent,
                Summary = success ? skill.SuccessDescription : skill.FailureDescription
            };
        }

        private static SkillRiskLevel Classify(int successRate)
        {
            if (successRate >= 85)
            {
                return SkillRiskLevel.Safe;
            }

            if (successRate >= 70)
            {
                return SkillRiskLevel.Low;
            }

            if (successRate >= 50)
            {
                return SkillRiskLevel.Medium;
            }

            if (successRate >= 30)
            {
                return SkillRiskLevel.High;
            }

            return SkillRiskLevel.Critical;
        }
    }
}
