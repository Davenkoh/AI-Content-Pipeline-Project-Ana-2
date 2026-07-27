#!/usr/bin/env python3
"""Stage the 6 Ana profile-picture gen bundles (refs + prompt) under chars/_gen/ana_pfp/.

Mirrors the evelyn_pfp run: each option gets to_upload/{1_hero,2_closeup,3_wardrobe,4_vary_angles,
5_background} + a prompt.txt built from the LOCKED recipe (knowledge/realism/
persona_gen_prompt_reference.md + the banked winner in winning_prompts.md §01).

  python3 chars/_gen/ana_pfp/stage.py
"""
import os, shutil, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
GEN = os.path.join(ROOT, "chars", "_gen", "ana_pfp")
BASE = os.path.join(ROOT, "character", "Ana", "Base References")
WARD = os.path.join(ROOT, "character", "_shared", "Wardrobe References")
LIB = os.path.join(ROOT, "media", "library")

HERO = os.path.join(BASE, "Ana_01_SOLO_hero-front .png")
CLOSEUP = os.path.join(BASE, "Ana_06_SOLO_face-closeup.png")
VARY = os.path.join(BASE, "Ana_02_SHEET_face-angles .png")

# Ana's locked identity, read off the hero + closeup — pasted into every prompt so the gen cannot
# drift her face while it is being told to un-airbrush the skin.
IDENTITY = (
    "IDENTITY: keep the same PERSON as reference images 1, 2 and 4 — the same Southeast-Asian "
    "(Vietnamese) woman with warm tan / golden-olive skin, the same soft oval face with high wide "
    "cheekbones, a gently rounded jaw and a softly pointed chin, the same wide-set warm dark-brown "
    "almond eyes with a shallow low double-eyelid crease and slightly hooded outer corners, the same "
    "straight softly-arched dark brows, the same straight nose with a slightly rounded tip and a "
    "moderately wide base, the same full lips with a defined cupid's bow, the same faint small beauty "
    "marks on her cheeks, and the same long dark brown-black hair — centre-parted with soft loose "
    "waves and fine face-framing strands (she must clearly read as the same individual) — but apply "
    "the real-skin notes above; do NOT beautify, whiten, brighten or slim her. The references are "
    "polished studio shots: dial the imperfection and warm tan tone back in."
)

SKIN = """SKIN & FACE — THIS IS THE #1 PRIORITY, MAKE IT REAL, NOT A BEAUTY FILTER. Her skin must NOT read white, bright, smooth or perfect:
- TONE: a warm natural TAN / golden-olive, lightly sun-kissed Southeast-Asian undertone — NOT a pale porcelain-white cast and NOT lightened. A whitened, evenly-pale face is the #1 filter tell. Keep it a natural warm medium-tan tone.
- BRIGHTNESS: expose her skin slightly UNDER — her face is NOT the brightest thing in the frame, no glow, no bloom, no luminous sheen on the skin. Dimmer and matte, not radiant.
- PORES & TEXTURE: clearly visible pores and real skin texture across the cheeks, nose, forehead, chin and chest. A fully MATTE finish (no dewy/glossy/waxy sheen). The attached references are polished studio shots — do NOT carry that finish over; this is a matte camera-roll photo.
- IMPERFECTIONS: a couple of small but visible blemishes/spots, slight redness around the nose and cheeks, a faint under-eye shadow — subtle, still attractive, never airbrushed away.
- FEATURE ASYMMETRY: her two eyes are noticeably a little different — ONE EYE slightly larger / a slightly different shape than the other, one brow set a touch higher, the mouth/almost-smile a little uneven side-to-side. NOT a flawless symmetric doll face.
- KILL the Mei Tu / beauty-filter look entirely: no whitening, no smoothing, no uniform glow, no plastic sheen.
- Emergency realism: candid, shot on a phone, slightly soft, subtle grain, imperfect exposure — like a friend's camera roll."""

PHONE = """WHOLE-FRAME PHONE CAPTURE: render it as ONE coherent consumer-iPhone exposure across subject and background — the entire frame a touch darker (about half a stop under), warm, colours natural and MUTED (not punchy/saturated). Reduce local contrast, digital clarity, highlight recovery and edge crispness. NO HDR pop, no cinematic grade, no fake bokeh, no heavy vignette. Ordinary 1080p detail, NOT razor 4K. Add subtle frame-wide luminance grain + faint chroma speckle in the shadows + a slight handheld micro-softness.

REAL DETAIL ONLY: do NOT invent scrambled letters, pseudo-logos, vague half-resolved faces/objects, or any detail that nearly resolves but does not. Real signage is either correctly spelled or naturally too soft to read; distant people/objects stay optically soft and small, never fake-sharpened into invented marks.

PHYSICAL INTEGRATION: she and the scene share ONE focal softness, grain, colour temperature, perspective, light direction and shadow density; her hair and clothing edges have ordinary phone softness with NO halo / cut-out ring; grounded contact with the scene and a matching cast/contact shadow; five correct fingers per hand, no distortion.

No text, captions, logos, or watermarks anywhere."""

TEMPLATE = """OUTPUT: a SQUARE 1:1 image (equal width and height), not a 3:4 portrait.

A candid SQUARE 1:1 phone photo of a young woman {scene_line}, framed as her social-media PROFILE PICTURE, taken by a friend a step away. It must look like a real photo from someone's camera roll, NOT a studio shoot, NOT a polished model render.

{skin}

{identity}

WARDROBE: dress her in the outfit shown in reference image 3 and match its styling closely — {wardrobe}. Real worn fabric with natural folds and a little movement. The neckline tastefully shows her neck, collarbone and shoulders. Keep her dainty thin gold layered necklace. {wardrobe_tail}

BACKGROUND — COPY REFERENCE IMAGE 5 LITERALLY, DO NOT INVENT: it is a REAL photo of the exact place — {background}. Reproduce THAT scene faithfully. Do NOT substitute any other location — {not_locations}. Place her naturally INTO it, {placement}, lit FROM that scene with matching shadows, perspective and natural phone depth-of-field. Never a cut-out pasted onto a backdrop.

COMPOSITION (profile-picture crop): a SQUARE 1:1 frame, zoomed to roughly the WAIST UP — she is the clear subject in the centre of the square but still set a little back, with the real scene filling the frame around and above her. A little headroom. Her face is clearly readable in the upper-centre. NOT a tight face crop and NOT a full-body shot.

POSE + EXPRESSION: candid and relaxed, NEVER a centered studio stare. {pose} Glancing softly just off to the side (not a hard dead-on stare), a small natural asymmetric almost-smile with a super-micro expression — a slight scrunch at the eyes and nose — one brow a touch higher. Caught mid-moment.

CAMERA EXPOSURE & LIGHT — GET THIS PHYSICALLY RIGHT: {light} Expose her about a stop UNDER so her skin reads matte, dim and tan, not glowing. One side of her face a touch darker. No blown highlights on the skin. There is no bright blown-white sky or light source directly behind her face.

BACKGROUND — MUST BE NON-UNIFORM: {nonuniform} all at DIFFERENT brightness, hue and saturation; some areas catch the light and bloom, some fall into soft shadow; real depth and a few real distant people. LITTER THE GROUND with random uncontrolled detail — {ground}. Not a clean even postcard.

{phone}
"""

OPTIONS = [
    dict(
        slug="opt1_hoian_lanterns",
        title="Hoi An Lanterns",
        bg=os.path.join(LIB, "vietnam-hoian", "8d71e265.jpg"),
        wardrobe=os.path.join(WARD, "8.png"),
        scene_line="at a silk-lantern shopfront in Hoi An Ancient Town, Vietnam",
        wardrobe_desc=(
            "a fitted white ribbed cotton cami / tank with thin straps and a small V neckline, worn "
            "with low-rise dark olive-green wide-leg jeans and fine layered gold chains with a small "
            "pendant"
        ),
        wardrobe_tail="Simple, casual Vietnam summer style — the outfit stays plain so the lanterns carry the colour.",
        background=(
            "a Hoi An lantern shop whose whole frontage is packed with hanging silk lanterns in dozens "
            "of colours — red, yellow, pink, blue, green, purple, orange — in tight overlapping rows "
            "filling the upper two thirds of the frame, some round, some tapered, some ribbed melon "
            "shapes; behind and between them the dim shop interior stacked with souvenir goods; a few "
            "ordinary real shoppers standing at the shopfront in everyday clothes; an old worn "
            "paved / tiled street floor in the foreground; daylight coming in from the open street"
        ),
        not_locations="no beach, no rice terraces, no bay, no temple, no night market street",
        placement=(
            "standing on the street just in front of the lantern wall, set back far enough that the "
            "packed lanterns read around and above her"
        ),
        pose="Turned slightly, one hand loose near her hair or reaching up toward a hanging lantern.",
        light=(
            "she is in the OPEN SHADE under the lantern canopy — soft, indirect, no direct sun on her "
            "face; the coloured lanterns behind her are the brightest, most saturated thing in the "
            "frame and cast faint warm colour bounce on her hair and shoulders."
        ),
        nonuniform=(
            "the lanterns, their frames and tassels, the dim shop interior, the goods on the shelves, "
            "the street floor and the distant shoppers"
        ),
        ground=(
            "worn uneven paving slabs, dirt and grit in the joints, scattered dry leaves, a stray "
            "electrical cable, scuff marks, a small plastic stool, a stray shadow"
        ),
    ),
    dict(
        slug="opt2_hanoi_tahien",
        title="Hanoi Night",
        bg=os.path.join(LIB, "vietnam-hanoi", "e6c7e3ba.jpg"),
        wardrobe=os.path.join(WARD, "2.png"),
        scene_line="on Ta Hien street in Hanoi's Old Quarter at night, Vietnam",
        wardrobe_desc=(
            "a black satin / silky spaghetti-strap slip cami with a soft square cowl neckline, worn "
            "with layered fine dark beaded and gold necklaces close at the throat"
        ),
        wardrobe_tail="Simple going-out night style.",
        background=(
            "a narrow Hanoi Old Quarter bar street at night — rows of small red and warm-white silk "
            "lanterns and bare bulbs strung along the shopfronts, an old painted bar facade with a "
            "cartoon-style painted mural and a hand-lettered sign, low plastic stools and small metal "
            "tables where real ordinary customers sit drinking beer, motorbikes parked tight against "
            "the wall, tangled overhead wires, the narrow street running away into more warm-lit bars "
            "and small shopfronts"
        ),
        not_locations="no beach, no bay, no rice terraces, no daytime street, no wide boulevard",
        placement=(
            "standing in the street among the tables, set a little back so the lantern-strung bar "
            "fronts and the alley depth read around and behind her"
        ),
        pose="Turned slightly, one shoulder toward camera, a hand loose near her necklace or hair.",
        light=(
            "warm tungsten lantern and bulb light coming from the SIDE and above — a real unlit night "
            "street, so the frame is genuinely DARK with deep shadows and only pools of warm light. "
            "No camera flash, no even fill. Her face catches a soft warm edge of that bar light and "
            "falls off quickly into shadow on the other side; visible night-time ISO noise in the "
            "shadows."
        ),
        nonuniform=(
            "the lanterns, bulbs, painted facade, plastic stools, parked motorbikes, seated customers "
            "and the dark alley behind"
        ),
        ground=(
            "wet-looking scuffed pavement, drain grates, cigarette ends, a crumpled napkin, chalk and "
            "tyre marks, a stray beer crate, small puddles reflecting the lanterns"
        ),
    ),
    dict(
        slug="opt3_halong_viewpoint",
        title="Ha Long Bay",
        bg=os.path.join(LIB, "vietnam-halong", "1254268a.jpg"),
        wardrobe=os.path.join(WARD, "16.png"),
        scene_line="at a hillside viewpoint over Ha Long Bay, Vietnam",
        wardrobe_desc=(
            "a blue-and-white paisley / bandana-print halter crop top tied behind the neck with the "
            "tie ends trailing, worn with low-rise washed dark-grey wide-leg jeans"
        ),
        wardrobe_tail="Summer boat-day style, a little sea breeze in the fabric and her hair.",
        background=(
            "a handheld viewpoint over Ha Long Bay — jade-green water below, big limestone karst "
            "islands with dense green scrub rising out of it, small white tour boats and a low "
            "floating pier on the water, thick tropical foliage and a leafy branch hanging into the "
            "top of the frame, more karsts fading into haze at the horizon"
        ),
        not_locations="no city street, no lanterns, no rice terraces, no sandy beach",
        placement=(
            "standing at the viewpoint edge in the shade of the overhanging foliage, set back so the "
            "bay, the karsts and the boats read behind and beside her — her head against the green "
            "karsts and water, NOT against the bright sky"
        ),
        pose="Turned slightly toward the bay, one hand pushing wind-blown hair off her face.",
        light=(
            "bright but HAZY tropical midday — she stands under the foliage in dappled open shade "
            "while the bay behind is the bright part of the frame; the sky is the brightest zone and "
            "sits well away from her face."
        ),
        nonuniform=(
            "the water, the karst faces, the scrub, the boats, the pier and the hazy horizon"
        ),
        ground=(
            "a dusty worn viewpoint path, loose stones and gravel, dry fallen leaves, trodden patchy "
            "grass, exposed roots, a stray shadow"
        ),
    ),
    dict(
        slug="opt4_sapa_terraces",
        title="Sapa Terraces",
        bg=os.path.join(LIB, "vietnam-sapa", "db403539.jpg"),
        wardrobe=os.path.join(WARD, "13.jpg"),
        scene_line="on a path above the rice terraces of the Muong Hoa valley in Sapa, Vietnam",
        wardrobe_desc=(
            "an oatmeal-cream chunky knit cardigan worn open and slipping off one shoulder over a "
            "taupe ribbed cami with thin straps, with baggy light-wash faded jeans"
        ),
        wardrobe_tail="Layered for cool damp mountain air.",
        background=(
            "the terraced rice fields of the Muong Hoa valley — long curved flooded terraces stepping "
            "down the hillside, their water reflecting the pale sky, wet mud walls between them, a "
            "couple of dark timber stilt farmhouses along the ridge, and layer after layer of "
            "blue-grey mountains dissolving into thick low mist behind, with a hazy diffused sun "
            "somewhere in the cloud"
        ),
        not_locations="no beach, no bay, no city street, no lanterns, no temple",
        placement=(
            "standing on the muddy path at the edge of the terraces, set back so the stepped flooded "
            "fields and the misted mountains read around and behind her"
        ),
        pose="Turned slightly, hands tucked into the cardigan or holding it closed at the chest.",
        light=(
            "soft, flat, cool MISTY mountain light — no hard sun anywhere, very low contrast, the "
            "distance washing out into fog. Absolutely no golden-hour wash on her face."
        ),
        nonuniform=(
            "the flooded terrace water, the mud walls, the green rice, the timber houses and the "
            "receding misted ridges"
        ),
        ground=(
            "a churned wet mud path with real footprints and boot marks, shallow puddles, cut rice "
            "stalks, weeds and grass tufts at the edges, loose small stones, splashed mud"
        ),
    ),
    dict(
        slug="opt5_anbang_beach",
        title="An Bang Beach",
        bg=os.path.join(LIB, "vietnam-anbang", "cda6cb1e.jpg"),
        wardrobe=os.path.join(WARD, "15.jpg"),
        scene_line="on An Bang Beach near Hoi An, Vietnam",
        wardrobe_desc=(
            "a soft white off-shoulder long-sleeve top with a loose draped, cascading ruffle front "
            "that bares the shoulders and collarbone, worn with baggy mid-blue jeans"
        ),
        wardrobe_tail="Breezy beach-walk style; the sea wind moves the fabric and her hair.",
        background=(
            "An Bang Beach on an overcast day — a row of thatched palm-leaf parasols and wooden "
            "sun-loungers set on pale grey-gold sand, a couple of real people lying on them, the "
            "grey-green sea with a low line of surf behind, a soft hazy overcast sky with broken "
            "cloud, and a faint dark headland far off on the horizon"
        ),
        not_locations="no city street, no lanterns, no rice terraces, no karst mountains, no blue tropical postcard sea",
        placement=(
            "standing on the sand between the parasols, set back so the loungers, the parasols and "
            "the sea read around and behind her"
        ),
        pose="Turned slightly, one hand catching wind-blown hair, the other loose at her side.",
        light=(
            "flat, soft, slightly cool OVERCAST beach light — a big even softbox sky, no sun, no "
            "golden hour, no hard shadows; her face matte and a touch dim under it."
        ),
        nonuniform=(
            "the thatch of the parasols, the wooden loungers, the wet and dry sand, the surf line, "
            "the sea and the broken cloud"
        ),
        ground=(
            "sand covered in real footprints and lounger drag-marks, scattered dry seaweed, small "
            "shells and pebbles, a stray plastic cup, twigs and a bit of washed-up litter, uneven "
            "damp and dry patches"
        ),
    ),
    dict(
        slug="opt6_trangan_boat",
        title="Trang An Boat",
        bg=os.path.join(LIB, "vietnam-ninhbinh", "5367c033.jpg"),
        wardrobe=os.path.join(WARD, "18.jpg"),
        scene_line="sitting in a small rowing boat on the river at Trang An, Ninh Binh, Vietnam",
        wardrobe_desc=(
            "a fitted burgundy / deep-red short-sleeve crew-neck tee with layered fine gold chains, "
            "worn with baggy dark-wash wide-leg jeans"
        ),
        wardrobe_tail="Simple, comfortable day-trip style — the red reads clearly against all the green.",
        background=(
            "the Trang An river in Ninh Binh seen from a low sampan — flat jade-green water, tall "
            "dark-green limestone karst mountains rising steeply close on both sides, a traditional "
            "multi-tiered dark wooden temple pavilion on stilts at the left bank, another small "
            "rowing sampan just ahead carrying real visitors in orange life jackets with a rower in a "
            "conical hat, dense jungle vegetation down to the waterline, and a bright overcast sky "
            "with broken cloud between the peaks"
        ),
        not_locations="no beach, no city street, no lanterns, no rice terraces, no open sea",
        placement=(
            "seated low in the boat with the river surface just below her, set back so the karsts, "
            "the pavilion and the water read around and behind her"
        ),
        pose=(
            "Seated and turned slightly, one hand resting on the boat rim, looking off toward the "
            "karsts."
        ),
        light=(
            "soft bright OVERCAST daylight with a faint cool green bounce coming up off the river "
            "onto her jaw and chest; no direct sun, no golden wash."
        ),
        nonuniform=(
            "the water, the karst rock faces, the jungle, the pavilion roofs, the boat ahead and its "
            "orange life jackets"
        ),
        ground=(
            "the worn painted metal-and-wood boat rim and floor right in the foreground — chipped "
            "paint, a wet floor, water drips and a small pool, a scuffed orange life jacket, a "
            "plastic bailing scoop, a coil of rope"
        ),
    ),
]


def stage(opt):
    d = os.path.join(GEN, opt["slug"])
    up = os.path.join(d, "to_upload")
    os.makedirs(up, exist_ok=True)
    for src, dst in [
        (HERO, "1_Ana_hero_front.png"),
        (CLOSEUP, "2_Ana_face_closeup.png"),
        (opt["wardrobe"], "3_wardrobe" + os.path.splitext(opt["wardrobe"])[1]),
        (VARY, "4_Ana_vary_angles.png"),
        (opt["bg"], "5_background.jpg"),
    ]:
        if not os.path.exists(src):
            sys.exit(f"missing ref: {src}")
        shutil.copy2(src, os.path.join(up, dst))
    prompt = TEMPLATE.format(
        scene_line=opt["scene_line"], skin=SKIN, identity=IDENTITY,
        wardrobe=opt["wardrobe_desc"], wardrobe_tail=opt["wardrobe_tail"],
        background=opt["background"], not_locations=opt["not_locations"],
        placement=opt["placement"], pose=opt["pose"], light=opt["light"],
        nonuniform=opt["nonuniform"], ground=opt["ground"], phone=PHONE,
    )
    with open(os.path.join(d, "prompt.txt"), "w") as f:
        f.write(prompt)
    with open(os.path.join(d, "title.txt"), "w") as f:      # run.sh names the output from this
        f.write(opt["title"] + "\n")
    print(f"  {opt['slug']:<24} -> {opt['title']:<16} refs=5  prompt={len(prompt)} chars")


if __name__ == "__main__":
    os.makedirs(GEN, exist_ok=True)
    print(f"[stage] Ana profile pictures — {len(OPTIONS)} options")
    for o in OPTIONS:
        stage(o)
