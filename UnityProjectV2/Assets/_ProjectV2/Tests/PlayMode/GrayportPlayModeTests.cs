using System.Collections;
using System.Linq;
using NUnit.Framework;
using ShadowOfTheUniverse.V2.Core;
using ShadowOfTheUniverse.V2.Runtime;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.UI;
#if UNITY_EDITOR
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
#endif

namespace ShadowOfTheUniverse.V2.Tests
{
    public sealed class GrayportPlayModeTests
    {
        [UnityTest]
        public IEnumerator AuthoredSceneWalkObjectiveExtractionAndRestart()
        {
#if UNITY_EDITOR
            EditorSceneManager.LoadSceneInPlayMode(
                "Assets/_ProjectV2/Generated/Levels/Grayport/Grayport_Blackout.unity",
                new LoadSceneParameters(LoadSceneMode.Single));
            yield return null;
            yield return null;
            var runtime = Object.FindAnyObjectByType<MissionRuntimeController>();
            Assert.That(runtime, Is.Not.Null);
            Assert.That(runtime.State.Map.Nodes.Count, Is.EqualTo(20));
            Assert.That(Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None).Length, Is.GreaterThan(480));
            Time.timeScale = 12;
            foreach (string id in new[] { "fork", "containers", "warehouse", "intel", "backgate", "relay_west", "relay" })
            {
                var node = Object.FindObjectsByType<NodeView>(FindObjectsSortMode.None).Single(n => n.NodeId == id);
                runtime.HandleNodeClicked(node);
                float deadline = Time.realtimeSinceStartup + 10;
                while (runtime.IsMoving && Time.realtimeSinceStartup < deadline) yield return null;
                Assert.That(runtime.IsMoving, Is.False, "Movement timed out: " + id);
                Assert.That(runtime.State.Units[0].CurrentNodeId, Is.EqualTo(id));
                if (id == "intel")
                {
                    Assert.That(runtime.InteractAtCurrentNode().Success, Is.True);
                    Assert.That(runtime.State.Encounters.ReconDownloaded, Is.True);
                }
            }
            CaptureRuntimeFrame();
            // Invoke the real UI binding once; finish with forced Core outcomes to keep the test deterministic.
            var unit = runtime.State.Units[0];
            var skill = unit.Skills.First(s => s.ObjectiveProgressOnSuccess == 1);
            Button actionButton = Object.FindObjectsByType<Button>(FindObjectsSortMode.None).Single(b => b.name == "Skill " + skill.Id);
            int budget = unit.CompromisePoints;
            Assert.That(actionButton.interactable, Is.True);
            actionButton.onClick.Invoke();
            Assert.That(unit.CompromisePoints, Is.EqualTo(budget - skill.CompromiseCost));
            while (runtime.State.ObjectiveProgress < runtime.State.ObjectiveRequired)
                MissionResolver.ApplySkillResolution(runtime.State, unit, RiskResolver.Resolve(unit, skill, 1));
            Assert.That(runtime.State.Outcome, Is.EqualTo(MissionOutcome.Running));
            MissionResolver.AdvanceTime(runtime.State, 8);
            Assert.That(runtime.State.Encounters.Phase, Is.EqualTo(TacticalPhase.Extraction));
            foreach (string id in new[] { "relay_east", "dock", "extract" })
            {
                var node = Object.FindObjectsByType<NodeView>(FindObjectsSortMode.None).Single(n => n.NodeId == id);
                runtime.HandleNodeClicked(node);
                float deadline = Time.realtimeSinceStartup + 10;
                while (runtime.IsMoving && Time.realtimeSinceStartup < deadline) yield return null;
                Assert.That(runtime.IsMoving, Is.False);
            }
            Assert.That(runtime.State.Outcome, Is.EqualTo(MissionOutcome.Victory));
            runtime.RestartMission();
            yield return null;
            Assert.That(runtime.State.Outcome, Is.EqualTo(MissionOutcome.Running));
            Assert.That(runtime.State.ObjectiveProgress, Is.Zero);
            Assert.That(runtime.State.Units[0].CurrentNodeId, Is.EqualTo("entry"));
            Assert.That(runtime.State.Units[0].RealityDebt, Is.Zero);
            Assert.That(runtime.State.Encounters.ReconDownloaded, Is.False);
            Assert.That(Object.FindObjectsByType<NodeView>(FindObjectsSortMode.None).Length, Is.EqualTo(20));
            Time.timeScale = 1;
            LogAssert.NoUnexpectedReceived();
#else
            yield return null;
            Assert.Ignore("Requires editor scene loading.");
#endif
        }

        [TearDown]
        public void RestoreClock() { Time.timeScale = 1; }

        private static void CaptureRuntimeFrame()
        {
            Camera camera=Camera.main;
            Canvas canvas=Object.FindAnyObjectByType<Canvas>();
            RenderMode oldMode=canvas.renderMode;
            Camera oldCamera=canvas.worldCamera;
            float oldDistance=canvas.planeDistance;
            RenderTexture oldActive=RenderTexture.active;
            var target=new RenderTexture(1600,1000,24);
            var image=new Texture2D(1600,1000,TextureFormat.RGB24,false);
            try
            {
                camera.targetTexture=target;
                canvas.renderMode=RenderMode.ScreenSpaceCamera;
                canvas.worldCamera=camera;
                canvas.planeDistance=1;
                Canvas.ForceUpdateCanvases();
                camera.Render();
                RenderTexture.active=target;
                image.ReadPixels(new Rect(0,0,1600,1000),0,0);
                image.Apply();
                System.IO.File.WriteAllBytes(System.IO.Path.GetFullPath(Application.dataPath+"/../../docs/grayport/unity-playmode.png"),image.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture=null;
                RenderTexture.active=oldActive;
                canvas.renderMode=oldMode;
                canvas.worldCamera=oldCamera;
                canvas.planeDistance=oldDistance;
                target.Release();
                Object.DestroyImmediate(target);
                Object.DestroyImmediate(image);
            }
        }
    }
}
