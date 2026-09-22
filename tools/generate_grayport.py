"""Deterministic, dependency-free Unity scene exporter for the Grayport level.

The same authored geometry is exported to a browser preview. The preview is not
a substitute for Unity import / Play Mode verification. No existing scene is replaced.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'UnityProjectV2'
ASSETS = PROJECT / 'Assets/_ProjectV2'
OUT = ASSETS / 'Generated/Levels/Grayport'
PREVIEW = ROOT / 'docs/grayport'
NS = uuid.UUID('be811165-9c4f-48fa-820e-c7083efe079d')
HEADER = '%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n'
PALETTE = {
    'water': '#163e50', 'wave': '#366b78', 'earth': '#263e46',
    'concrete': '#768487', 'road': '#35474e', 'line': '#d4bd85',
    'steel': '#314950', 'roof': '#496471', 'wall': '#a3adb0',
    'orange': '#c17c4b', 'teal': '#3d898b', 'blue': '#47778c',
    'red': '#a64c43', 'dark': '#20303b', 'glass': '#69c8d0',
    'light': '#ffe0a0', 'green': '#68d9ae', 'white': '#d9e8dd',
    'rock': '#506367', 'sand': '#9e9b83', 'warning': '#f1af54',
}
objects = []


def guid(key):
    return uuid.uuid5(NS, key).hex


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8', newline='\n')


def meta(path, kind='asset'):
    key = path.relative_to(PROJECT).as_posix()
    dst = Path(str(path) + '.meta')
    if dst.exists():
        return re.search(r'guid: (\w+)', dst.read_text()).group(1)
    g = guid(key)
    extra = 'folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n' if kind == 'folder' else ''
    write(dst, f'fileFormatVersion: 2\nguid: {g}\n{extra}')
    return g


def box(name, pos, scale, mat, rot=(0, 0, 0), solid=False):
    objects.append(dict(name=name, position=list(pos), scale=list(scale),
                        rotation=list(rot), material=mat, solid=solid))


def beam(name, a, b, width, mat, depth=None):
    d = [b[i] - a[i] for i in range(3)]
    length = math.sqrt(sum(v*v for v in d))
    yaw = math.degrees(math.atan2(d[0], d[2]))
    pitch = -math.degrees(math.atan2(d[1], math.hypot(d[0], d[2])))
    box(name, [(a[i]+b[i])/2 for i in range(3)], (width, depth or width, length), mat, (pitch, yaw, 0))


def node(id, label, x, z, y=1.02, danger=0):
    return dict(id=id, label=label, position=[x, y, z], danger=danger)


NODES = [
    node('entry', '01 / LANDING', -34, -24), node('fork', 'ACCESS', -24, -16),
    node('gate', 'FRONT GATE', -12, -16, danger=1),
    node('checkpoint', 'CHECKPOINT', 4, -16, danger=2),
    node('ramp', 'RELAY APPROACH', 17, -11), node('relay_front', 'SOUTH RAMP', 17, 2, 4.02),
    node('relay', '05 / RELAY', 17, 8, 4.02, 2),
    node('relay_west', 'WEST RAMP', 11, 12, 4.02), node('relay_east', 'EAST RAMP', 23, 8, 4.02),
    node('containers', '02 / CONTAINER YARD', -26, -2), node('warehouse', 'WAREHOUSE', -23, 16),
    node('intel', 'RECON TERMINAL', -8, 16), node('backgate', 'REAR ACCESS', 8, 16),
    node('shore', 'COASTAL WALK', -36, -10), node('coast', 'SEAWALL', -36, 12),
    node('maintenance', '04 / MAINTENANCE', -30, 26), node('power', 'POWER CONTROL', -14, 26),
    node('rear', 'SERVICE ACCESS', 8, 26), node('dock', '06 / DOCK', 35, 8),
    node('extract', 'EXTRACTION', 52, 8),
]
ND = {n['id']: n for n in NODES}
for n in NODES:
    n['exposure'] = 1 if n['id'] in ['gate', 'checkpoint', 'dock'] else 0
    n['cover'] = 1 if n['id'] in ['containers', 'warehouse', 'intel', 'backgate'] else 0
    n['poweredGuard'] = n['id'] in ['checkpoint', 'dock']
    n['interaction'] = 1 if n['id'] == 'intel' else 2 if n['id'] == 'power' else 0
PATROLS = [
    dict(id='Gate watch', nodes=['gate','checkpoint','ramp','checkpoint'], secondsPerLeg=12, offset=0, extractionOnly=False),
    dict(id='Yard watch', nodes=['containers','warehouse','intel','warehouse'], secondsPerLeg=14, offset=7, extractionOnly=False),
    dict(id='Pier response', nodes=['dock','relay_east','dock','extract'], secondsPerLeg=10, offset=0, extractionOnly=True),
]
ROUTES = []


def chain(ids, kind):
    for a, b in zip(ids, ids[1:]):
        ROUTES.append(dict(a=a, b=b, kind=kind))


chain(['entry', 'fork', 'gate', 'checkpoint', 'ramp', 'relay_front', 'relay'], 'direct')
chain(['fork', 'containers', 'warehouse', 'intel', 'backgate', 'relay_west', 'relay'], 'cover')
chain(['entry', 'shore', 'coast', 'maintenance', 'power', 'rear', 'backgate'], 'service')
chain(['relay', 'relay_east', 'dock', 'extract'], 'extract')
chain(['checkpoint', 'dock'], 'direct')
chain(['coast', 'warehouse'], 'cover')


def building(name, x, z, w, d, height, material='wall'):
    box(name, (x, 1+height/2, z), (w, height, d), material, solid=True)
    box(name+' roof', (x, 1+height+.25, z), (w+.5, .5, d+.5), 'roof')
    for xx in [-w*.32, 0, w*.32]:
        box(name+' window', (x+xx, 1+height*.7, z-d/2-.035), (w*.18, .8, .08), 'glass')
    box(name+' door', (x, 2.1, z-d/2-.06), (1.8, 2.2, .1), 'dark')
    box(name+' vent', (x+w*.22, 1+height+.7, z), (1.8, .6, 1.6), 'steel')


def container(x, z, mat, y=1):
    box('Cargo container', (x, y+1.25, z), (3.4, 2.5, 7), mat, solid=True)
    for dz in range(-3, 4):
        for dx in [-1.73, 1.73]:
            box('Container rib', (x+dx, y+1.3, z+dz), (.08, 2.35, .1), 'steel')
    for dx in [-.85, .85]:
        box('Container door lock', (x+dx, y+1.2, z-3.54), (.08, 2.1, .1), 'white')


def lamp(x, z, h=6):
    box('Quay lamp mast', (x, 1+h/2, z), (.16, h, .16), 'steel')
    box('Quay lamp arm', (x+.6, 1+h, z), (1.4, .15, .15), 'steel')
    box('Quay lamp lens', (x+1.2, h+.95, z), (.65, .12, .45), 'light')


def create_geometry():
    box('Harbor water', (0, -1.35, 0), (160, .3, 125), 'water')
    box('Port foundation', (1, -1.2, 2), (84, 4.4, 66), 'earth')
    box('Quay pavement', (1, .78, 2), (84, .44, 66), 'concrete')
    box('Landing beach', (-34, -.08, -31), (17, .7, 11), 'sand')
    box('Landing ramp', (-34, .4, -27), (5, .3, 9), 'concrete', (-8, 0, 0))
    box('Dock deck', (48, .7, 8), (24, .6, 9), 'concrete')
    for x in range(39, 61, 4):
        for z in [4, 12]:
            box('Pier pile', (x, -1.7, z), (.7, 4.4, .7), 'steel')
            box('Pier bollard', (x, 1.28, z), (.55, .55, .55), 'warning')
    # The raised relay platform has three matching inclined approach road meshes.
    box('Relay raised platform', (17, 2, 8), (12, 4, 12), 'concrete')
    for r in ROUTES:
        a, b = ND[r['a']]['position'][:], ND[r['b']]['position'][:]
        beam('Road '+r['a']+' to '+r['b'], a, b, 3.8 if r['kind']=='direct' else 2.6, 'road', .18)
        # Painted broken center lines remain geometry, not debug graph edges.
        dist = math.dist(a,b)
        if r['kind'] in ['direct', 'extract']:
            for i in range(1, int(dist/3)):
                t = i*3/dist
                p = [a[k]+(b[k]-a[k])*t for k in range(3)]
                q = [a[k]+(b[k]-a[k])*(t+.9/dist) for k in range(3)]
                p[1] += .115; q[1] += .115
                beam('Road paint', p, q, .10, 'line', .025)
    # Structural quay walls and water streaks.
    for x in range(-40, 44, 3):
        for z in [-31.1, 35.1]:
            box('Quay face buttress', (x, -1, z), (.4, 4, .5), 'steel')
    for i in range(45):
        x = -74+(i*19 % 145); z = -54+(i*31 % 104)
        if -43 < x < 64 and -34 < z < 38:
            continue
        box('Water glint', (x, -1.18, z), (2+(i%4), .025, .12), 'wave')
    for x,z in [(-32,-4),(-20,-3),(-15,5),(-30,8),(-19,8),(-8,-4),(-2,-4)]:
        container(x,z,['teal','orange','blue'][(x+z)%3])
    container(-15,5,'red',3.5)
    building('Warehouse A', -10, 8, 11, 8, 6)
    building('Warehouse B', -26, 20.5, 7, 4.5, 4)
    building('Maintenance workshop', -23, 31, 10, 5, 3.5, 'teal')
    building('Guard house', -4, -22, 6, 5, 3)
    building('Relay control', 20, 11, 4, 3, 5, 'wall')
    # Tall radio mast behind the objective, built from open steelwork.
    for x in [19,23]:
        for z in [10,13]:
            beam('Radio tower leg', (x,4,z), (21+(x-21)*.22,23,11.5+(z-11.5)*.22), .22,'steel')
    for h in [8,12,16,20]:
        beam('Radio tower cross brace',(19,h,10),(23,h+3,13),.12,'steel')
        box('Radio platform',(21,h,11.5),(4.4,.16,3.6),'steel')
    box('Antenna spine',(21,25,11.5),(.14,5,.14),'white')
    box('Antenna signal lamp',(21,27.7,11.5),(.45,.45,.45),'red')
    box('Relay console',(17,4.6,9),(1.2,1.2,.8),'teal')
    box('Relay console display',(17,5,8.55),(.9,.4,.05),'glass')
    # Cargo crane landmark; its legs stay clear of the extraction road.
    for x in [32,39]:
        for z in [18,24]:
            beam('Crane leg',(x,1,z),(x,15,z),.5,'orange')
    for z in [18,24]:
        beam('Crane top beam',(30,15,z),(52,15,z),.7,'orange')
        for x in range(31,52,3):
            beam('Crane truss',(x,15,z),(x+2,17,z),.18,'line')
    beam('Crane cross beam',(32,15,18),(32,15,24),.8,'orange')
    beam('Crane cross beam',(48,15,18),(48,15,24),.8,'orange')
    box('Crane cabin',(38,14,21),(3,2.4,3),'teal')
    box('Crane cabin glass',(38,14.3,19.45),(2.6,1.2,.1),'glass')
    beam('Crane cable',(47,15,21),(47,3.5,21),.08,'dark')
    box('Crane hook',(47,3.2,21),(1,.7,.6),'warning')
    # Work areas, barriers, utility boxes and road lighting.
    for x in [-18,-14,-10,-6,-2,2,6,10]:
        box('South fence post',(x,2,-28),(.15,2,.15),'steel')
        box('South fence rail',(x+1.9,2.5,-28),(3.8,.12,.12),'steel')
    for x,z in [(-28,-18),(-10,-19),(3,-19),(11,-15),(9,20),(-33,23),(30,5),(40,12)]:
        lamp(x,z)
    for x,z in [(-22,1),(-20,12),(-3,18),(3,-12),(30,11)]:
        box('Concrete cover',(x,1.65,z),(3,1.3,.7),'concrete',solid=True)
    for x,z in [(-8,17),(-14,27)]:
        box('Utility terminal',(x,1.8,z),(1.2,1.6,.7),'teal')
        box('Terminal screen',(x,2.1,z-.38),(.8,.55,.06),'glass')
    for i in range(5):
        box('Substation transformer',(-5+i*3,2.5,31),(1.8,3,2),'steel',solid=True)
        box('Transformer cap',(-5+i*3,4.3,31),(.7,.6,.7),'light')
    for x in [15,21,27,33]:
        for z in [-25,-20]:
            box('Parking bay stripe',(x,1.03,z),(4,.035,.1),'line')
    for x,z in [(17,-24),(23,-24),(29,-24),(34,-16),(33,-4),(38,-4)]:
        box('Dock freight crate',(x,1.7,z),(2,1.4,2),'orange',solid=True)
        for dx in [-.65,.65]:
            box('Crate strap',(x+dx,2.43,z),(.12,.06,2.05),'steel')
    # Extraction craft sits beside, not on, the usable pier.
    box('Extraction boat hull',(52,-.1,17),(4.8,1.6,9),'dark')
    box('Extraction boat deck',(52,.8,17),(4.2,.3,8),'white')
    box('Extraction boat cabin',(52,1.9,18),(3,2,3),'teal')
    box('Boat windshield',(52,2.2,16.45),(2.5,.8,.08),'glass')
    for dx in [-2,2]:
        box('Extraction light',(52+dx,1.1,8),(.35,.2,2),'green')
    box('Landing boat hull',(-36,-.1,-38),(4,1.2,7),'dark',(0,20,0))
    # Small rocks define the landing shoreline without blocking the path.
    for i in range(12):
        x=-43+(i*7%18); z=-35-(i%3)
        box('Shore rock',(x,-.3,z),(1.6+i%3,1.5,1.8),'rock',(15,i*31,12))


def q_euler(e):
    x,y,z = [math.radians(v)/2 for v in e]
    # Unity Quaternion.Euler applies Z then X then Y.
    sx,cx,sy,cy,sz,cz = math.sin(x),math.cos(x),math.sin(y),math.cos(y),math.sin(z),math.cos(z)
    return [cy*sx*cz+sy*cx*sz, sy*cx*cz-cy*sx*sz, cy*cx*sz-sy*sx*cz, cy*cx*cz+sy*sx*sz]


def vec(v, keys='xyz'):
    return '{'+', '.join(f'{k}: {n:.7g}' for k,n in zip(keys,v))+'}'


class Scene:
    def __init__(self):
        old=(ASSETS/'Scenes/V2_MVP.unity').read_text(encoding='utf-8')
        self.parts=[old.split('--- !u!1 &100000')[0].replace('m_AmbientMode: 0','m_AmbientMode: 3')]
        self.roots=[]
        self.next=1000

    def obj(self, name, pos=(0,0,0), scale=(1,1,1), rot=(0,0,0), components=(), tag='Untagged'):
        g=self.next; self.next+=20
        self.roots.append(g+1)
        common='  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {fileID: 0}\n  m_PrefabInstance: {fileID: 0}\n  m_PrefabAsset: {fileID: 0}\n'
        self.parts.append(f'--- !u!1 &{g}\nGameObject:\n'+common+'  serializedVersion: 6\n  m_Component:\n'+''.join(f'  - component: {{fileID: {g+c}}}\n' for c in [1]+[c[0] for c in components])+f'  m_Layer: 0\n  m_Name: {json.dumps(name)}\n  m_TagString: {tag}\n  m_IsActive: 1\n')
        self.parts.append(f'--- !u!4 &{g+1}\nTransform:\n'+common+f'  m_GameObject: {{fileID: {g}}}\n  serializedVersion: 2\n  m_LocalRotation: {vec(q_euler(rot),"xyzw")}\n  m_LocalPosition: {vec(pos)}\n  m_LocalScale: {vec(scale)}\n  m_Children: []\n  m_Father: {{fileID: 0}}\n  m_LocalEulerAnglesHint: {vec(rot)}\n')
        for offset,typ,cls,data in components:
            self.parts.append(f'--- !u!{typ} &{g+offset}\n{cls}:\n'+common+f'  m_GameObject: {{fileID: {g}}}\n'+data)
        return g

    def geometry(self,o):
        material=guid('Assets/_ProjectV2/Generated/Levels/Grayport/Materials/'+o['material']+'.mat')
        self.obj(o['name'],o['position'],o['scale'],o['rotation'],[
            (2,33,'MeshFilter','  m_Mesh: {fileID: 10202, guid: 0000000000000000e000000000000000, type: 0}\n'),
            (3,23,'MeshRenderer',f'  m_Enabled: 1\n  m_CastShadows: 1\n  m_ReceiveShadows: 1\n  m_Materials:\n  - {{fileID: 2100000, guid: {material}, type: 2}}\n  m_SortingLayerID: 0\n  m_SortingOrder: 0\n')])

    def mono(self,name,script,fields,pos=(0,0,0)):
        return self.obj(name,pos,components=[(4,114,'MonoBehaviour',f'  m_Enabled: 1\n  m_EditorHideFlags: 0\n  m_Script: {{fileID: 11500000, guid: {script}, type: 3}}\n  m_Name: \n  m_EditorClassIdentifier: \n'+fields)])

    def save(self,path):
        self.parts.append('--- !u!1660057539 &9223372036854775807\nSceneRoots:\n  m_ObjectHideFlags: 0\n  m_Roots:\n'+''.join(f'  - {{fileID: {r}}}\n' for r in self.roots))
        write(path,''.join(self.parts)); meta(path)


def existing_guid(path):
    return re.search(r'guid: (\w+)',Path(str(path)+'.meta').read_text()).group(1)


def so(path,script,name,fields):
    body=f'--- !u!114 &11400000\nMonoBehaviour:\n  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {{fileID: 0}}\n  m_PrefabInstance: {{fileID: 0}}\n  m_PrefabAsset: {{fileID: 0}}\n  m_GameObject: {{fileID: 0}}\n  m_Enabled: 1\n  m_EditorHideFlags: 0\n  m_Script: {{fileID: 11500000, guid: {existing_guid(script)}, type: 3}}\n  m_Name: {name}\n  m_EditorClassIdentifier: \n'
    write(path,HEADER+body+fields)
    return meta(path)


def create_assets():
    for name,color in PALETTE.items():
        rgb=[int(color[i:i+2],16)/255 for i in [1,3,5]]
        p=OUT/'Materials'/f'{name}.mat'
        write(p,HEADER+f'''--- !u!21 &2100000
Material:
  serializedVersion: 8
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: Grayport_{name}
  m_Shader: {{fileID: 46, guid: 0000000000000000f000000000000000, type: 0}}
  m_ValidKeywords: []
  m_InvalidKeywords: []
  m_LightmapFlags: 4
  m_EnableInstancingVariants: 1
  m_DoubleSidedGI: 0
  m_CustomRenderQueue: -1
  stringTagMap: {{}}
  disabledShaderPasses: []
  m_SavedProperties:
    serializedVersion: 3
    m_TexEnvs: []
    m_Ints: []
    m_Floats:
    - _Glossiness: 0.25
    - _Metallic: 0.1
    m_Colors:
    - _Color: {vec(rgb+[1], 'rgba')}
''')
        meta(p)
    fields='  nodes:\n'
    for n in NODES:
        x,y,z=n['position']
        fields+=f'  - nodeId: {n["id"]}\n    displayName: {n["label"]}\n    terrain: 2\n    owner: {2 if n["id"]=="relay" else 0}\n    dangerLevel: {n["danger"]}\n    position: {{x: {x}, y: {z}}}\n    elevation: {y}\n'
        fields+=f'    exposure: {n["exposure"]}\n    coverRating: {n["cover"]}\n    poweredGuard: {int(n["poweredGuard"])}\n    interaction: {n["interaction"]}\n'
    fields+='  routes:\n'+''.join(f'  - fromNodeId: {r["a"]}\n    toNodeId: {r["b"]}\n    routeType: 0\n' for r in ROUTES)
    mg=so(OUT/'Grayport_Map.asset',ASSETS/'Scripts/Data/NodeMapSO.cs','Grayport_Map',fields)
    skill_guids=[]
    for original,cost in [('HeatShift',10),('StaticLock',24)]:
        source=(ASSETS/'SampleData'/f'V2Skill_{original}.asset').read_text()
        fields='  skillId:'+source.split('  skillId:',1)[1].rstrip()+f'\n  compromiseCost: {cost}\n'
        skill_guids.append(so(OUT/f'Grayport_{original}.asset',ASSETS/'Scripts/Data/SkillDataSO.cs',f'Grayport_{original}',fields))
    ug=so(OUT/'Grayport_Operator.asset',ASSETS/'Scripts/Data/UnitDataSO.cs','Grayport_Operator',
          '  unitId: grayport_operator\n  displayName: Operator / Echo\n  domain: 0\n  scale: 1\n  movementRange: 2\n  maxHealth: 100\n  skills:\n'+''.join(f'  - {{fileID: 11400000, guid: {g}, type: 2}}\n' for g in skill_guids))
    patrol_fields='  tacticalEncountersEnabled: 1\n  patrols:\n'
    for p in PATROLS:
        patrol_fields+=f'  - Id: {p["id"]}\n    Nodes:\n'+''.join(f'    - {n}\n' for n in p['nodes'])+f'    SecondsPerLeg: {p["secondsPerLeg"]}\n    PhaseOffsetSeconds: {p["offset"]}\n    ExtractionOnly: {int(p["extractionOnly"])}\n'
    mission=so(OUT/'Grayport_Mission.asset',ASSETS/'Scripts/Data/TacticalMissionSO.cs','Grayport_Mission',f'''  missionId: grayport_blackout
  displayName: GRAYPORT / BLACKOUT
  missionType: 0
  briefingText: Choose an approach. Disable the relay on the raised platform, then reach the east pier. Cyan terminals provide recon and power control.
  timeLimitSeconds: 300
  maxAlertLevel: 5
  objectiveRequired: 3
  startingCompromisePoints: 100
  targetNodeId: relay
  extractionNodeId: extract
  nodeMap: {{fileID: 11400000, guid: {mg}, type: 2}}
  startingUnits:
  - unit: {{fileID: 11400000, guid: {ug}, type: 2}}
    startNodeId: entry
'''+patrol_fields)
    bg=so(OUT/'Grayport_Bootstrap.asset',ASSETS/'Scripts/Data/MissionBootstrapConfigSO.cs','Grayport_Bootstrap',f'  defaultMission: {{fileID: 11400000, guid: {mission}, type: 2}}\n  secondsPerMove: 1\n')
    return bg


def create_scene(bg):
    s=Scene()
    for o in objects:
        s.geometry(o)
    s.mono('Grayport Mission Runtime',existing_guid(ASSETS/'Scripts/Runtime/MissionRuntimeController.cs'),f'  bootstrapConfig: {{fileID: 11400000, guid: {bg}, type: 2}}\n  authoredEnvironment: 1\n  movementSpeed: 9\n  secondsPerMove: 0\n')
    s.mono('Grayport Camera and Controls',existing_guid(ASSETS/'Scripts/Runtime/GrayportPresentation.cs'),'')
    s.obj('Main Camera',(77,95,-100),rot=(38, -36, 0),tag='MainCamera',components=[(2,20,'Camera','''  m_Enabled: 1
  serializedVersion: 2
  m_ClearFlags: 2
  m_BackGroundColor: {r: 0.045, g: 0.085, b: 0.11, a: 1}
  m_projectionMatrixMode: 1
  m_GateFitMode: 2
  m_FOVAxisMode: 0
  m_SensorSize: {x: 36, y: 24}
  m_LensShift: {x: 0, y: 0}
  m_FocalLength: 50
  m_NormalizedViewPortRect: {serializedVersion: 2, x: 0, y: 0, width: 1, height: 1}
  near clip plane: 0.3
  far clip plane: 500
  field of view: 60
  orthographic: 1
  orthographic size: 58
  m_Depth: -1
  m_CullingMask: {serializedVersion: 2, m_Bits: 4294967295}
  m_RenderingPath: -1
  m_TargetTexture: {fileID: 0}
  m_TargetDisplay: 0
  m_TargetEye: 3
  m_HDR: 1
  m_AllowMSAA: 1
''')])
    s.obj('Harbor Moon',(0,50,0),rot=(48,-28,0),components=[(2,108,'Light','''  m_Enabled: 1
  serializedVersion: 11
  m_Type: 1
  m_Color: {r: 0.8, g: 0.9, b: 1, a: 1}
  m_Intensity: 1.4
  m_Range: 10
  m_SpotAngle: 30
  m_Shadows:
    m_Type: 2
    m_Resolution: 2
    m_Strength: 0.65
    m_Bias: 0.05
    m_NormalBias: 0.4
    m_NearPlane: 0.2
  m_CullingMask: {serializedVersion: 2, m_Bits: 4294967295}
  m_RenderingLayerMask: 1
  m_Lightmapping: 4
''')])
    s.save(OUT/'Grayport_Blackout.unity')


def validate(data):
    ids={n['id'] for n in NODES}
    assert len(ids)==len(NODES)
    seen={'entry'}
    while True:
        more={r['b'] for r in ROUTES if r['a'] in seen}|{r['a'] for r in ROUTES if r['b'] in seen}
        if more <= seen: break
        seen |= more
    assert seen == ids, 'Disconnected graph'
    assert all(r['a'] in ids and r['b'] in ids for r in ROUTES)
    assert len({tuple(sorted((r['a'],r['b']))) for r in ROUTES})==len(ROUTES)
    # All solid buildings must leave the authored walking centerline clear.
    collisions=[]
    for r in ROUTES:
        a,b=ND[r['a']]['position'],ND[r['b']]['position']
        for o in objects:
            if not o['solid']: continue
            p,sz=o['position'],o['scale']
            for i in range(101):
                t=i/100
                v=[a[k]+(b[k]-a[k])*t for k in range(3)]
                if abs(v[0]-p[0])<sz[0]/2+.45 and abs(v[2]-p[2])<sz[2]/2+.45 and v[1]<p[1]+sz[1]/2:
                    collisions.append(f'{r["a"]}->{r["b"]}: {o["name"]} at {p}')
                    break
    if collisions: raise AssertionError('\n'.join(collisions))
    return dict(status='static_checks_passed',nodes=len(NODES),routes=len(ROUTES),geometry_objects=len(objects),
                centerline_obstruction_count=0,unity_import='not_checked_by_static_generator',play_mode='not_run',
                geometry_sha256=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest())


def main():
    create_geometry()
    data=dict(title='GRAYPORT / BLACKOUT',palette=PALETTE,objects=objects,nodes=NODES,routes=ROUTES,patrols=PATROLS)
    report=validate(data)
    bg=create_assets(); create_scene(bg)
    write(OUT/'grayport-layout.json',json.dumps(data,ensure_ascii=False,indent=2)); meta(OUT/'grayport-layout.json')
    write(PREVIEW/'layout.js','window.GRAYPORT = '+json.dumps(data,ensure_ascii=False)+';\n')
    write(PREVIEW/'validation.json',json.dumps(report,indent=2)+'\n')
    for folder in [ASSETS/'Generated',ASSETS/'Generated/Levels',OUT,OUT/'Materials']:
        meta(folder,'folder')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
