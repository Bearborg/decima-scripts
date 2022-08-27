from typing import List, Set
import pydecima
from pydecima.resources import CharacterDescriptionComponentResource, FacialAnimationComponentResource,\
    FocusScannedInfo, FocusTargetComponentResource, HumanoidBodyVariant, HumanoidBodyVariantGroup, SpawnSetup,\
    SpawnSetupGroup, VoiceComponentResource
import os
from pydecima.enums import ETextLanguages

game_root_file = os.path.join(os.path.dirname(__file__), r'hzd_root_path.txt')
name_map = {"ambert": "Amber Trujillo",
            "anis": "Ani Sava",
            "armona": "Amron Adams",
            "arvins": "Arvin Singh",
            "ashleya": "Ashley Sales",
            "babyaloy": "Unknown",
            # "bahavas": "Gary Terranova (heavily edited)",
            "barbarap": "Barbara Pergament",
            "barryb": "Unknown (listed as BarryB)",
            # "bast_child": "Quinne Daniels (edited)",
            "belitae": "Belita Edwards",
            "billyc": "Billy Collins",
            "briceh": "Brice Haiden",
            "caitlinm": "Caitlin Myers",
            "camilal": "Camila Llano",
            "catherinew": "Catherine Werner",
            # "catherinew_hologram": "Catherine Werner",
            "chadwicka": "Chadwick Armstrong",
            "chaseb": "Chase Baker",
            "chooks": "Chook Sibtain",
            "chuckm": "Chuck Maytum",
            "courtneym": "Courtney McCullough",
            "danceswiththunderjaw": "Unknown (listed as DancesWithThunderjaw)",
            "davids": "David Saucedo",
            # "dervahl": "John Freeman (edited)",
            "eddyp": "Eddy Panos de Los Angeles",
            "elizabethc": "Elizabeth Clare",
            # "elizabeths_hologram": "Hannah Hoekstra (possibly)",
            "emilyb": "Emily Bader",
            "eugene": "Eugene Wood",
            "eugene_hologram": "Eugene Wood",
            "francisd": "Francis Duggan",
            # "francisd_hologram": "Francis Duggan",
            # "gaia": "Kari Bel (edited)",
            "garyt": "Gary Terranova",
            "giyamis": "Unknown (listed as GiyamiS)",
            "hannah": "Hannah Hoekstra",
            "hayden": "Hayden Mclean",
            "henkp": "Unknown (listed as HenkP)",
            "henrovmakarov": "Henry Mark (heavily edited, listed under the fake name HenrovMakarov)",
            "henrym": "Henry Mark",
            "jackies": "Jackie Shea",
            "jayd": "Jay Dersahagian",
            "jaylaf": "Jayla Franklin",
            "jaymcl": "Jay McLeod",
            "jaymcl_hologram": "Jay McLeod",
            "jedidahf": "Jedidah Fernandez-Doqui",
            "jenm": "Jen Morillo",
            "joelc": "Joel Cavness",
            "johnf": "John Freeman",
            "johnh": "John Hopkins",
            "kangj": "Kang-Ja Holohan (possibly - listed as 'KangJa')",
            "kareng": "Karen Guzman",
            "karib": "Kari Bel",
            "katiem": "Katie-Mae Sheridan",
            "keiths": "Keith Somers",
            # "keiths_hologram": "Keith Somers",
            "kennetha": "Kenneth Atkins",
            "kennethb": "Kenneth Bloom",
            "kirkn": "Kirk Newmann",
            "kirkovnabatov": "Kirk Newmann (heavily edited, listed under the fake name KirkovNabatov)",
            "krisb": "Kris Branch",
            # "krisb_hologram": "Kris Branch",
            "larar": "Lara Rossi",
            "leilaw": "Leila Wong",
            "levyt": "Levy Tran",
            "lindsayj": "Lindsay Jensen",
            "lloydo": "Lloyd Owen",
            # "lloydo_hologram": "Lloyd Owen",
            "lorena": "Lorena Andrea (possibly - listed as 'Lorena')",
            "marcusb": "Marcus Borga",
            "markk": "Mark Kosakura",
            "markp": "Mark Powley",
            "markpyoung": "Mark Powley",
            "marlenem": "Marlene Marquez",
            "melissam": "Melissa Mars",
            "michaelm": "Michael Marrio",
            "mickeyg": "Mikey Grand",
            "mireyg": "Mirey Gerber",
            # "mireyg_hologram": "Mirey Gerber",
            "nicoles": "Nicole Stone",
            "nicolettem": "Nicolette McKenzie",
            "nikitap": "Nikita Petrov",
            "ojio": "Oji Osuga",
            # "ojio_hologram": "Oji Osuga",
            "owend": "Owen Hunte",
            "pelek": "Pele Kizy",
            # "petra": "Lindsay Jensen (edited)",
            "quinned": "Quinne Daniels",
            "robertd": "Robert Don",
            "sachikoh": "Sachiko Hirairi",
            "sachikovsmekhov": "Sachiko Hirairi (heavily edited, listed under the fake name SachikovSmekhov)",
            "samanthat": "Samantha Totem",
            # "samanthat_hologram": "Samantha Totem",
            # "sona": "Jen Morillo (edited)",
            "soniap": "Sonia Pleasant",
            "steveo": "Steve Ortega",
            "sylens": "Lance Reddick",
            # "sylens_hologram": "Lance Reddick",
            "takuyai": "Takuya Iba",
            # "tebold": "Francis Duggan (edited)",
            # "tebyoung": "Francis Duggan (edited)",
            "tianab": "Tiana Belle",
            "tonyp": "Tony Panterra",
            "treborwhalestick": "Unknown (listed as TreborWhaleStick)",
            "tyeo": "Tye Olson",
            # "vala": "Jedidah Fernandez-Doqui (edited)",
            "yddegoosebibs": "Unknown (listed as YddeGooseBibs)",
            "zirah": "Zairah"}


def get_names(setup: SpawnSetup, script_objects):
    names: Set[str] = set()
    for x in map(lambda v: v.follow(script_objects), setup.unk_refs_3):
        if isinstance(x, VoiceComponentResource):
            for voice_signal in x.voice_signals:
                names.add(voice_signal.follow(script_objects)
                                      .voice.follow(script_objects)
                                      .text.follow(script_objects).language[ETextLanguages.English])
        if isinstance(x, FocusTargetComponentResource):
            names.add(x.focus_scanned_info
                      .follow(script_objects).title
                      .follow(script_objects).language[ETextLanguages.English])
        if isinstance(x, FocusScannedInfo):
            names.add(x.title.follow(script_objects).language[ETextLanguages.English])
        if isinstance(x, CharacterDescriptionComponentResource):
            names.add(x.character_name.follow(script_objects).language[ETextLanguages.English])
    return names


def get_face_from_body_variant(variant: HumanoidBodyVariant, script_objects):
    print(' {}'.format(variant))
    facrs = filter(lambda f: f.follow(script_objects).type == 'FacialAnimationComponentResource', variant.unk_refs_1)
    for z in facrs:
        obj: FacialAnimationComponentResource = z.follow(script_objects)
        facr = ''
        if obj.name != 'FacialAnimationComponentResource':
            facr_name = obj.name[5:] if obj.name.startswith('FACR_') else obj.name
            facr = ' - {}'.format(facr_name)
        filenames = set()
        for ref in [z, obj.head_grp_multimesh, obj.face_rig_data, obj.skeleton, obj.neutral_anim]:
            if ref.type == 2:
                paths = ref.path.split('/')
                if 'animation' in paths:
                    name = paths[paths.index('animation') - 1]
                    filenames.add(name[:-9] if name.endswith('_hologram') else name)
        model_names = list()
        for name in filenames:
            model_names.append(name_map[name] if name in name_map else "!!{}".format(name))
        print('   {}{}'.format(model_names[0] if len(model_names) == 1 else model_names, facr))


def get_faces(spawn_file, script_objects):
    pydecima.reader.read_objects(spawn_file, script_objects)
    names = set()
    spawn_groups = [x for x in script_objects.values() if isinstance(x, SpawnSetupGroup)]
    variants: Set[HumanoidBodyVariant] = set()

    def spawn_setup_is_weird(spawn, objects):
        return spawn.humanoid_body_variant.follow(objects).name == 'Nora_Child_Group'

    # logic for dealing with weird conditional in some nora spawnsetups that replaces them with children(???)
    spawn_setups: List[SpawnSetup] = []
    if len(spawn_groups) > 0:
        for x in spawn_groups:
            group_setups = map(lambda v: v.unk_ref.follow(script_objects), x.unk_structs)
            group_setups = filter(lambda v: isinstance(v, SpawnSetup)
                                  and v.humanoid_body_variant.type != 0
                                  and not spawn_setup_is_weird(v, script_objects), group_setups)
            spawn_setups += list(group_setups)
    else:
        spawn_setups = list(filter(lambda v: isinstance(v, SpawnSetup)
                                   and v.humanoid_body_variant.type != 0, script_objects.copy().values()))

    for x in spawn_setups:
        names = names.union(get_names(x, script_objects))
        body_variant = x.humanoid_body_variant.follow(script_objects)
        if isinstance(body_variant, HumanoidBodyVariantGroup):
            variants = variants.union({v.follow(script_objects) for v in body_variant.body_variants})
        elif isinstance(body_variant, HumanoidBodyVariant):
            variants.add(body_variant)
        else:
            assert False
    print(names)
    for y in sorted(list(variants), key=lambda v: v.name):
        get_face_from_body_variant(y, script_objects)


def dump_all(path):
    script_objects = {}
    for root, dnames, fnames in os.walk(path):
        for f in fnames:
            script_objects.clear()
            print(f, end=' ')
            get_faces(os.path.join(root, f), script_objects)


pydecima.reader.set_globals(_game_root_file=game_root_file, _decima_version='HZDPC')
dump_all(os.path.join(pydecima.reader.game_root, r'entities/spawnsetups/characters'))
dump_all(os.path.join(pydecima.reader.game_root, r'entities/dlc1/spawnsetups/characters'))
