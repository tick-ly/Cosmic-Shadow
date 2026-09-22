"""Verify native YAML references, geometry identity, and deterministic rebuilding."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'UnityProjectV2/Assets/_ProjectV2'
OUT=BASE/'Generated/Levels/Grayport'


def load_unity(path):
    text=path.read_text(encoding='utf-8')
    normalized=re.sub(r'^%.*\n','',text,flags=re.M)
    normalized=re.sub(r'^--- !u!\d+ &\d+', '---', normalized,flags=re.M)
    return list(yaml.safe_load_all(normalized))


def hashes():
    return {p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in OUT.rglob('*') if p.is_file()}


def main():
    before=hashes()
    subprocess.run([sys.executable,str(ROOT/'tools/generate_grayport.py')],check=True,capture_output=True)
    assert hashes()==before,'Rebuild altered asset bytes or GUIDs'
    guid_paths={}
    for p in BASE.rglob('*.meta'):
        g=re.search(r'^guid: (\w+)',p.read_text(encoding='utf-8-sig'),re.M)
        if not g: continue
        assert g[1] not in guid_paths, f'Duplicate GUID {p}'
        guid_paths[g[1]]=p
    missing=[]
    for p in OUT.rglob('*'):
        if not p.is_file() or p.suffix not in {'.unity','.asset','.mat'}: continue
        load_unity(p)
        assert Path(str(p)+'.meta').exists(), f'Missing meta: {p}'
        for g in re.findall(r'guid: (\w+)',p.read_text()):
            if g.startswith('0000000000000000'): continue
            if g not in guid_paths: missing.append((str(p),g))
    assert not missing,missing
    scene=OUT/'Grayport_Blackout.unity'
    text=scene.read_text()
    ids=re.findall(r'^--- !u!\d+ &(\d+)',text,re.M)
    assert len(ids)==len(set(ids)), 'Duplicate scene file IDs'
    for ref in re.findall(r'\{fileID: (\d+)\}',text):
        assert ref=='0' or ref in ids, f'Missing local scene reference {ref}'
    docs=load_unity(scene)
    transforms=[d['Transform'] for d in docs if 'Transform' in d]
    layout=json.loads((OUT/'grayport-layout.json').read_text())
    # Exported static geometry precedes camera and runtime objects.
    for source,actual in zip(layout['objects'],transforms):
        for field,key in [('position','m_LocalPosition'),('scale','m_LocalScale')]:
            values=[actual[key][k] for k in 'xyz']
            assert all(abs(a-b)<1e-4 for a,b in zip(values,source[field])),source['name']
    assert len([d for d in docs if 'MeshRenderer' in d])==len(layout['objects'])
    map_asset=load_unity(OUT/'Grayport_Map.asset')[0]['MonoBehaviour']
    assert len(map_asset['nodes'])==len(layout['nodes'])
    for source,target in zip(layout['nodes'],map_asset['nodes']):
        assert source['id']==target['nodeId']
        assert source['exposure']==target['exposure'] and source['cover']==target['coverRating']
        assert source['interaction']==target['interaction'] and source['poweredGuard']==bool(target['poweredGuard'])
        assert source['position']==[target['position']['x'],target['elevation'],target['position']['y']]
    mission=load_unity(OUT/'Grayport_Mission.asset')[0]['MonoBehaviour']
    assert mission['tacticalEncountersEnabled']==1
    assert mission['targetNodeId']=='relay' and mission['extractionNodeId']=='extract'
    assert mission['timeLimitSeconds']==300 and mission['maxAlertLevel']==5 and mission['objectiveRequired']==3
    assert len(mission['patrols'])==len(layout['patrols'])
    route_pairs={tuple(sorted((r['a'],r['b']))) for r in layout['routes']}
    for source,target in zip(layout['patrols'],mission['patrols']):
        assert source['nodes']==target['Nodes'] and source['secondsPerLeg']==target['SecondsPerLeg']
        assert source['offset']==target['PhaseOffsetSeconds'] and source['extractionOnly']==bool(target['ExtractionOnly'])
        cycle=source['nodes']+[source['nodes'][0]]
        assert all(tuple(sorted((a,b))) in route_pairs for a,b in zip(cycle,cycle[1:])),source['id']
    for name,cost in [('HeatShift',10),('StaticLock',24)]:
        assert load_unity(OUT/f'Grayport_{name}.asset')[0]['MonoBehaviour']['compromiseCost']==cost
    report=dict(status='passed',scene_documents=len(docs),geometry_objects=len(layout['objects']),
                referenced_guids_resolved=True,local_file_ids_resolved=True,
                encounter_config_matches_preview=True,patrol_edges_valid=True,skill_budget_config_valid=True,
                scene_geometry_matches_preview=True,repeat_generation_byte_identical=True,
                unity_import='pending',play_mode='pending')
    (ROOT/'docs/grayport/asset-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        (ROOT/'docs/grayport/asset-checks.json').write_text(json.dumps(dict(status='failed',error=str(exc)),indent=2)+'\n')
        raise
