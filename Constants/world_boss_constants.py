# globals.py or similar
wb_shared_cooldowns: dict[int, float] = {}  # {guild_id: last_post_time}

class WBEmojis:
    Gmax = "<:gigantamax:1300780191710314496>"
    Sgmax = "<:shinygigantamax:1300780198085656627>"
    WB_Spawn = "<:world_boss_spawned:1300780186073170051>"
    eet = "<:eet:1570724060428767232>"


class WBGuide:
    alcremie = "!wbalc"
    appletun = "!wbapp"
    blastoise = "!wbbla"
    butterfree = "!wbbut"
    centiskorch = "!wbcen"
    charizard = "!wbcha"
    coalossal = "!wbcoa"
    cinderace = "!wbcin"
    copperajah = "!wbcop"
    corviknight = "!wbcor"
    drednaw = "!wbdre"
    duraludon = "!wbdur"
    eternatus = "!wbeet"
    eevee = "!wbeev"
    flapple = "!wbfla"
    garbodor = "!wbgar"
    gengar = "!wbgen"
    grimmsnarl = "!wbgri"
    hatterene = "!wbhat"
    inteleon = "!wbint"
    kingler = "!wbkin"
    lapras = "!wblap"
    machamp = "!wbmac"
    melmetal = "!wbmel"
    meowth = "!wbmeo"
    orbeetle = "!wborb"
    pikachu = "!wbpik"
    rillaboom = "!wbril"
    sandaconda = "!wbsan"
    snorlax = "!wbsno"
    toxtricity = "!wbtox"
    urs = "!wburs"
    uss = "!wbuss"
    venusaur = "!wbven"


class WBRegImage:
    alcremie = "https://play.pokemonshowdown.com/sprites/xyani/alcremie-gmax.gif?quality=lossless"
    appletun = "https://play.pokemonshowdown.com/sprites/xyani/flapple-gmax.gif?quality=lossless"
    blastoise = "https://cdn.discordapp.com/attachments/1202428993408868373/1251459949176033330/blastoise_gmax.gif"
    butterfree = "https://play.pokemonshowdown.com/sprites/xyani/butterfree-gmax.gif?quality=lossless"
    centiskorch = "https://play.pokemonshowdown.com/sprites/xyani/centiskorch-gmax.gif?quality=lossless"
    charizard = "https://play.pokemonshowdown.com/sprites/xyani/charizard-gmax.gif?quality=lossless"
    coalossal = "https://play.pokemonshowdown.com/sprites/xyani/coalossal-gmax.gif?quality=lossless"
    cinderace = "https://cdn.discordapp.com/attachments/965340186500296737/965367587078799440/cinderace-gmax.gif"
    copperajah = "https://play.pokemonshowdown.com/sprites/xyani/copperajah-gmax.gif?quality=lossless"
    corviknight = "https://play.pokemonshowdown.com/sprites/xyani/corviknight-gmax.gif?quality=lossless"
    drednaw = "https://play.pokemonshowdown.com/sprites/xyani/drednaw-gmax.gif?quality=lossless"
    duraludon = "https://play.pokemonshowdown.com/sprites/xyani/duraludon-gmax.gif?quality=lossless"
    eternatus = "https://play.pokemonshowdown.com/sprites/xyani/eternatus-eternamax.gif"
    eevee = (
        "https://play.pokemonshowdown.com/sprites/xyani/eevee-gmax.gif?quality=lossless"
    )
    flapple = "https://play.pokemonshowdown.com/sprites/xyani/flapple-gmax.gif?quality=lossless"
    garbodor = "https://play.pokemonshowdown.com/sprites/xyani/garbodor-gmax.gif?quality=lossless"
    gengar = "https://play.pokemonshowdown.com/sprites/xyani/gengar-gmax.gif?quality=lossless"
    grimmsnarl = "https://cdn.discordapp.com/attachments/1249277613198016555/1257478367482089473/gigantamax-grimmsnarl.gif"
    hatterene = "https://play.pokemonshowdown.com/sprites/xyani/hatterene-gmax.gif?quality=lossless"
    inteleon = "https://play.pokemonshowdown.com/sprites/xyani/inteleon-gmax.gif?quality=lossless"
    kingler = "https://play.pokemonshowdown.com/sprites/xyani/kingler-gmax.gif?quality=lossless"
    lapras = "https://play.pokemonshowdown.com/sprites/xyani/lapras-gmax.gif?quality=lossless"
    machamp = "https://play.pokemonshowdown.com/sprites/xyani/machamp-gmax.gif?quality=lossless"
    melmetal = "https://play.pokemonshowdown.com/sprites/xyani/melmetal-gmax.gif?quality=lossless"
    meowth = "https://play.pokemonshowdown.com/sprites/xyani/meowth-gmax.gif?quality=lossless"
    orbeetle = "https://play.pokemonshowdown.com/sprites/xyani/orbeetle-gmax.gif?quality=lossless"
    pikachu = "https://play.pokemonshowdown.com/sprites/xyani/pikachu-gmax.gif?quality=lossless"
    rillaboom = "https://cdn.discordapp.com/attachments/1249277613198016555/1258898040517955605/gigantamax-rillaboom.gif"
    sandaconda = "https://play.pokemonshowdown.com/sprites/xyani/sandaconda-gmax.gif?quality=lossless"
    snorlax = "https://play.pokemonshowdown.com/sprites/xyani/snorlax-gmax.gif?quality=lossless"
    toxtricity = "https://play.pokemonshowdown.com/sprites/xyani/toxtricity-gmax.gif?quality=lossless"
    urs = "https://cdn.discordapp.com/attachments/1260532287729045530/1268354938455724154/gigantamax-urshifu-rapidstrike.gif"
    uss = "https://cdn.discordapp.com/attachments/1260532287729045530/1266174031577481337/gigantamax-urshifu-singlestrike.gif"
    venusaur = "https://cdn.discordapp.com/attachments/1249277613198016555/1251897414391037992/venusaur-gmax.gif"


class WBShinyImage:
    alcremie = "https://play.pokemonshowdown.com/sprites/xyani/alcremie-gmax.gif?quality=lossless"
    appletun = "https://play.pokemonshowdown.com/sprites/ani-shiny/flapple-gmax.gif?quality=lossless"
    blastoise = "https://cdn.discordapp.com/attachments/1202428993408868373/1251458589470494791/shiny_blastoise_gmax.gif"
    butterfree = "https://cdn.discordapp.com/attachments/1249277613198016555/1251901445700325489/shiny-butterfree-gmax.gif"
    centiskorch = "https://play.pokemonshowdown.com/sprites/ani-shiny/centiskorch-gmax.gif?quality=lossless"
    charizard = "https://play.pokemonshowdown.com/sprites/ani-shiny/charizard-gmax.gif?quality=lossless"
    coalossal = "https://play.pokemonshowdown.com/sprites/ani-shiny/coalossal-gmax.gif?quality=lossless"
    cinderace = "https://cdn.discordapp.com/attachments/1202428993408868373/1249206765971574815/shiny_cinderace_gmax.gif"
    copperajah = "https://play.pokemonshowdown.com/sprites/ani-shiny/copperajah-gmax.gif?quality=lossless"
    corviknight = "https://cdn.discordapp.com/attachments/1249277613198016555/1253638780209070091/corviknight-gmax.gif"
    drednaw = "https://play.pokemonshowdown.com/sprites/ani-shiny/drednaw-gmax.gif?quality=lossless"
    duraludon = "https://cdn.discordapp.com/attachments/1260532287729045530/1260552740539469844/shiny-gigantamax-duraludon.gif"
    eternatus = (
        "https://play.pokemonshowdown.com/sprites/ani-shiny/eternatus-eternamax.gif"
    )
    eevee = "https://play.pokemonshowdown.com/sprites/ani-shiny/eevee-gmax.gif?quality=lossless"
    flapple = "https://play.pokemonshowdown.com/sprites/ani-shiny/flapple-gmax.gif?quality=lossless"
    garbodor = "https://play.pokemonshowdown.com/sprites/ani-shiny/garbodor-gmax.gif?quality=lossless"
    gengar = "https://play.pokemonshowdown.com/sprites/ani-shiny/gengar-gmax.gif?quality=lossless"
    grimmsnarl = "https://cdn.discordapp.com/attachments/1249277613198016555/1257477533956313170/shiny-gigantamax-grimmsnarl.gif"
    hatterene = "https://play.pokemonshowdown.com/sprites/ani-shiny/hatterene-gmax.gif?quality=lossless"
    inteleon = "https://play.pokemonshowdown.com/sprites/ani-shiny/inteleon-gmax.gif?quality=lossless"
    kingler = "https://play.pokemonshowdown.com/sprites/ani-shiny/kingler-gmax.gif?quality=lossless"
    lapras = "https://play.pokemonshowdown.com/sprites/ani-shiny/lapras-gmax.gif?quality=lossless"
    machamp = "https://play.pokemonshowdown.com/sprites/ani-shiny/machamp-gmax.gif?quality=lossless"
    melmetal = "https://play.pokemonshowdown.com/sprites/ani-shiny/melmetal-gmax.gif?quality=lossless"
    meowth = "https://play.pokemonshowdown.com/sprites/ani-shiny/meowth-gmax.gif?quality=lossless"
    orbeetle = "https://play.pokemonshowdown.com/sprites/ani-shiny/orbeetle-gmax.gif?quality=lossless"
    pikachu = "https://play.pokemonshowdown.com/sprites/ani-shiny/pikachu-gmax.gif?quality=lossless"
    rillaboom = "https://cdn.discordapp.com/attachments/1249277613198016555/1258898058364588186/shiny-gigantamax-rillaboom.gif"
    sandaconda = "https://play.pokemonshowdown.com/sprites/ani-shiny/sandaconda-gmax.gif?quality=lossless"
    snorlax = "https://play.pokemonshowdown.com/sprites/ani-shiny/snorlax-gmax.gif?quality=lossless"
    toxtricity = "https://play.pokemonshowdown.com/sprites/ani-shiny/toxtricity-gmax.gif?quality=lossless"
    urs = "https://cdn.discordapp.com/attachments/1260532287729045530/1268355584126746644/shiny-gigantamax-urshifu-rapidstrike.gif"
    uss = "https://cdn.discordapp.com/attachments/1260532287729045530/1266173393934221333/gigantamax-urshifu-singlestrike.gif?ex=67cb7f5d&is=67ca2ddd&hm=7bef59af3139536fffdbec5d6598d0aa3c8ad33de6b5686a8be47d4897de2621&"
    venusaur = "https://cdn.discordapp.com/attachments/1249277613198016555/1251896812348899448/shiny-venusaur-gmax.gif"


class WBColors:
    Shiny = 16561340
    alcremie = 12631228
    appletun = 12728890
    blastoise = 4498092
    butterfree = 10512608
    centiskorch = 15023424
    charizard = 16286264
    coalossal = 2695470
    cinderace = 16155932
    copperajah = 4090192
    corviknight = 1841723
    drednaw = 5806756
    duraludon = 8687269
    eternatus = 4077189
    eevee = 13739114
    flapple = 12728890
    garbodor = 6652779
    gengar = 9468064
    grimmsnarl = 2303037
    hatterene = 12378098
    inteleon = 7715797
    kingler = 14182448
    lapras = 5415901
    machamp = 10526920
    melmetal = 8026746
    meowth = 15784064
    orbeetle = 14885153
    pikachu = 16306512
    rillaboom = 426303
    sandaconda = 8479062
    snorlax = 4221048
    toxtricity = 9982907
    urs = 2308234
    uss = 13762560
    venusaur = 9026706


class WB_RegDex:
    alc = "7193"
    app = "7241"
    bla = "7160"
    but = "7166"
    cen = "7211"
    cha = "7145"
    coa = "7199"
    cin = "7148"
    cop = "7226"
    cor = "7184"
    dre = "7223"
    dur = "7214"
    eet = "7244"
    eev = "7154"
    fla = "7229"
    gar = "7190"
    gen = "7151"
    gri = "7202"
    hat = "7238"
    int = "7217"
    kin = "7181"
    lap = "7175"
    mac = "7157"
    mel = "7187"
    meo = "7172"
    orb = "7220"
    pik = "7169"
    ril = "7205"
    san = "7208"
    sno = "7178"
    tox = "7196"
    urs = "7232"
    uss = "7235"
    ven = "7163"


class WB_RegHeaderIcon:
    alc = "https://media.discordapp.net/attachments/1385036679756386395/1385103609968201800/alcremie-gmax3.png?ex=689967c2&is=68981642&hm=107dca20df95113fc38b93ae9a23280c086595f5b7d762bc6caff0fb221fb1b1&=&format=webp&quality=lossless&width=28&height=50"
    app = "https://media.discordapp.net/attachments/1385036679756386395/1385105705815638026/flapple-gmax3.png?ex=689969b6&is=68981836&hm=0c9e4ab1471b35539a317ffd2e136f5759bd525c1ca45a87dd5cda0c31dff663&=&format=webp&quality=lossless&width=29&height=33"
    bla = "https://media.discordapp.net/attachments/1385036679756386395/1385044700683174008/blastoise-gmax3.png?ex=6899d9a5&is=68988825&hm=80c05774e15ebf884b676618c0ebcde7ab0bab5f02d5b48358d0f6fcfd417a36&=&format=webp&quality=lossless&width=32&height=34"
    but = "https://media.discordapp.net/attachments/1385036679756386395/1385107480551624845/butterfree-gmax3.png?ex=68996b5d&is=689819dd&hm=ca27bd9f47554034832417aed24af2dde8dbaf9abf2b677f1a23bf1042ac94c4&=&format=webp&quality=lossless&width=34&height=27"
    cen = "https://media.discordapp.net/attachments/1385036679756386395/1385047670904717313/centiskorch-gmax6.png?ex=6899dc69&is=68988ae9&hm=9df9405a1692bafc859fe3bc51e65c0f837e94e5c6d93d1fbf680f72af270123&=&format=webp&quality=lossless&width=50&height=39"
    cha = "https://media.discordapp.net/attachments/1385036679756386395/1385037658840891493/charizard-gmax3.png?ex=6899d316&is=68988196&hm=e676090dad85576252f5f136e2a57b0e76cc2b5f05eee80114f8b752dbd67a41&=&format=webp&quality=lossless&width=50&height=46"
    coa = "https://media.discordapp.net/attachments/1385036679756386395/1385109468832075820/coalossal-gmax3.png?ex=68996d37&is=68981bb7&hm=a31e6ec3dbcbfc9ecd152f92d02cf671128aa98ba7899d15abf2275edd22de7d&=&format=webp&quality=lossless&width=42&height=50"
    cin = "https://media.discordapp.net/attachments/1385036679756386395/1385056246784200714/cinderace-gmax3.png?ex=6899e466&is=689892e6&hm=1d4dddbf634964d09687a93820d1a5b1e4bb14eb07677280b99d134b2ffbaf8d&=&format=webp&quality=lossless&width=42&height=50"
    cop = "https://media.discordapp.net/attachments/1385036679756386395/1385111621617188985/copperajah-gmax3.png?ex=68996f38&is=68981db8&hm=51defb3a861dbaaf58bbd57b231ef1ba99a9238f4202066e29d84e184bbe05db&=&format=webp&quality=lossless&width=36&height=50"
    cor = "https://media.discordapp.net/attachments/1385036679756386395/1385219173415653437/corviknight-gmax3.png?ex=6899d363&is=689881e3&hm=6db9adb83dc294b59c88f5ee63300c80741e94280f32ec712b836139e9c1e2c3&=&format=webp&quality=lossless&width=50&height=45"
    dre = "https://media.discordapp.net/attachments/1385036679756386395/1385061753443844286/drednaw-gmax3.png?ex=6899e987&is=68989807&hm=f9fdda7cd8d59cc9c17abe5ae6c2cce3d6c2b6f4ca2efa34ec6a778fcad9cd58&=&format=webp&quality=lossless&width=25&height=28"
    dur = "https://media.discordapp.net/attachments/1385036679756386395/1385062909473722379/duraludon-gmax3.png?ex=6899ea9a&is=6898991a&hm=a7814f19a8befffeeded34d150ede6f92cc673b4a0b7c5421c81692542a825dc&=&format=webp&quality=lossless&width=39&height=50"
    eet = "https://media.discordapp.net/attachments/1385036679756386395/1385064802526957658/1334523596990582804.png?ex=6899ec5e&is=68989ade&hm=cf43b263374332c962294d54af88d7821015e3efb36c8aca85c691cbf4675107&=&format=webp&quality=lossless&width=64&height=70"
    eev = "https://media.discordapp.net/attachments/1385036679756386395/1385066374530994260/eevee-gmax3.png?ex=6899edd4&is=68989c54&hm=06b1a48736f04f502a0d73a9ab87e178e257fdc5734878eb0010c3084efadd0f&=&format=webp&quality=lossless&width=25&height=26"
    fla = "https://media.discordapp.net/attachments/1385036679756386395/1385105705815638026/flapple-gmax3.png?ex=689969b6&is=68981836&hm=0c9e4ab1471b35539a317ffd2e136f5759bd525c1ca45a87dd5cda0c31dff663&=&format=webp&quality=lossless&width=29&height=33"
    gar = "https://media.discordapp.net/attachments/1385036679756386395/1385067492665331812/garbodor-gmax3.png?ex=6899eedf&is=68989d5f&hm=e527b3937d52c6f591071dfb6c0fe6c0ae7c4ff1b5459903636294e3e48cd666&=&format=webp&quality=lossless&width=36&height=30"
    gen = "https://media.discordapp.net/attachments/1385036679756386395/1385069242617167964/gengar-gmax3.png?ex=689947c0&is=6897f640&hm=27249f11738d9a5d027dc59eed54a721067a720338eb4bbd471afcb14c25e2ba&=&format=webp&quality=lossless&width=35&height=26"
    gri = "https://media.discordapp.net/attachments/1385036679756386395/1385221571987243089/grimmsnarl-gmax3.png?ex=6899d59e&is=6898841e&hm=40159cbfef8e282ec6ccd333c5d2d2a64bb6bb388530af0d05f419445a518858&=&format=webp&quality=lossless&width=34&height=50"
    hat = "https://media.discordapp.net/attachments/1385036679756386395/1385222607619625030/hatterene-gmax3.png?ex=6899d695&is=68988515&hm=c00c79f0939045d1a55963bf3dac3789c771fc728ebaf07bdf5fa499d5121043&=&format=webp&quality=lossless&width=32&height=50"
    int = "https://media.discordapp.net/attachments/1385036679756386395/1385070107188789308/inteleon-gmax6.png?ex=6899488e&is=6897f70e&hm=be5c9d48c8d77ae0e06580c399a3d9f04d44350bb41365320d0092adc921e8bd&=&format=webp&quality=lossless&width=23&height=50"
    kin = "https://media.discordapp.net/attachments/1385036679756386395/1385071581801484400/kingler-gmax3.png?ex=689949ee&is=6897f86e&hm=5414c608ef8368d9a6617e947f48fb02a7128def99e19d04355c6c81c320eafe&=&format=webp&quality=lossless&width=34&height=34"
    lap = "https://media.discordapp.net/attachments/1385036679756386395/1385074278042439820/lapras-gmax3.png?ex=68994c71&is=6897faf1&hm=6aab022c388c23833bc26528bfea573310ac7b6d2fe9911d8d0c5f1383c35020&=&format=webp&quality=lossless&width=28&height=27"
    mac = "https://media.discordapp.net/attachments/1385036679756386395/1385075610832867413/machamp-gmax3.png?ex=68994daf&is=6897fc2f&hm=7c4ab0cfcf99a8931c1232f57e3dce905fe15bb2e2a93f72f5323627fa107b47&=&format=webp&quality=lossless&width=30&height=30"
    mel = "https://media.discordapp.net/attachments/1385036679756386395/1385112512692879390/melmetal-gmax3.png?ex=6899700d&is=68981e8d&hm=33914108a10a8fbcf89a4b084f6ea02ad8eb35fff5e8fad43cda3c51c9d8a045&=&format=webp&quality=lossless&width=50&height=42"
    meo = "https://media.discordapp.net/attachments/1385036679756386395/1385095178565587015/meowth-gmax3.png?ex=68995fe8&is=68980e68&hm=9bae9949adc04d4edb972b84fc049a7fedbb6f4a867e91454809c4528de990d4&=&format=webp&quality=lossless&width=29&height=37"
    orb = "https://media.discordapp.net/attachments/1385036679756386395/1385224693174239272/orbeetle-gmax3.png?ex=6899d887&is=68988707&hm=72111bc601b17554eaa23b927e2e28228347cecc6919a3031eccfa90f859ea12&=&format=webp&quality=lossless&width=44&height=36"
    pik = "https://media.discordapp.net/attachments/1385036679756386395/1385095817123205120/pikachu-gmax3.png?ex=68996080&is=68980f00&hm=037a12bd86dad212707fac50d4b366fa6cacd8248c1c640678d8ba6bd4945f0e&=&format=webp&quality=lossless&width=23&height=28"
    ril = "https://media.discordapp.net/attachments/1385036679756386395/1385096760313253919/rillaboom-gmax3.png?ex=68996161&is=68980fe1&hm=c8793944c952ba04a199651d97d5c05bd6d9ced254cd885c8c7cc5a0a8a2bc84&=&format=webp&quality=lossless&width=50&height=41"
    san = "https://media.discordapp.net/attachments/1385036679756386395/1385097621340946493/sandaconda-gmax3.png?ex=6899622e&is=689810ae&hm=03ec5154676b0f0a8bc2fe91ab3b24c2cc6616b5247616aa53bed40b2eb965ec&=&format=webp&quality=lossless&width=37&height=41"
    sno = "https://media.discordapp.net/attachments/1385036679756386395/1385098531777544332/snorlax-gmax3.png?ex=68996307&is=68981187&hm=093abaa28ddcb860e4cc2afe94efd29f7dd0950585e2d5d064d74a204ed76294&=&format=webp&quality=lossless&width=35&height=33"
    tox = "https://media.discordapp.net/attachments/1385036679756386395/1385099619897446490/toxtricity-gmax3.png?ex=6899640b&is=6898128b&hm=864a010b58dd04f5e98224a952d428ec95949b42a95d983d276d01a785a317c6&=&format=webp&quality=lossless&width=36&height=41"
    urs = "https://media.discordapp.net/attachments/1385036679756386395/1385100586319609926/urshifu-rapid-strike-gmax3.png?ex=689964f1&is=68981371&hm=9aebf47efa2bc3fc96257fd9f838c474b0fd418fcddbf71f855a346d4a00a9d0&=&format=webp&quality=lossless&width=44&height=50"
    uss = "https://media.discordapp.net/attachments/1385036679756386395/1385223453824782426/urshifu-gmax3.png?ex=6899d75f&is=689885df&hm=a79951db3304dafce1f09e6b400018cb738cabc8f819f0d5faa573cc5d36367c&=&format=webp&quality=lossless&width=42&height=50"
    ven = "https://media.discordapp.net/attachments/1385036679756386395/1385101164860932241/venusaur-gmax3.png?ex=6899657b&is=689813fb&hm=ac415ecf18a5b722be79764075f4d43c2d407330a45b4b8233ba498f43c1338d&=&format=webp&quality=lossless&width=33&height=34"


class WB_ShinyHeaderIcon:
    alc = "https://media.discordapp.net/attachments/1385036679756386395/1385103610169262110/alcremie-gmax6.png?ex=689967c2&is=68981642&hm=68072ae5c3e25a393db614ab8736c1ef43ce716e7a00226579d7efe231962b55&=&format=webp&quality=lossless&width=28&height=50"
    app = "https://media.discordapp.net/attachments/1385036679756386395/1385105706058780743/flapple-gmax6.png?ex=689969b6&is=68981836&hm=d06c07e53e9b130b08ff724b7158b84955ee549b41b5f62160f1b8430bbfa19d&=&format=webp&quality=lossless&width=29&height=33"
    bla = "https://media.discordapp.net/attachments/1385036679756386395/1385044700922122312/blastoise-gmax6.png?ex=6899d9a5&is=68988825&hm=e4d70842866c411607c0a386880be685f868b45f7c997baa7771fbf425983796&=&format=webp&quality=lossless&width=32&height=34"
    but = "https://media.discordapp.net/attachments/1385036679756386395/1385107480836571177/butterfree-gmax6.png?ex=68996b5d&is=689819dd&hm=8bddc828fa207c44697a366625d309572dee1d2bf54fee4ea98be9ea9e867a6a&=&format=webp&quality=lossless&width=34&height=27"
    cen = "https://media.discordapp.net/attachments/1385036679756386395/1385047671177216040/centiskorch-gmax3.png?ex=6899dc69&is=68988ae9&hm=0052c339bdde60925b59bdd565628a5be8ffed7ec38ada3b30096cb4a367e69d&=&format=webp&quality=lossless&width=50&height=39"
    cha = "https://media.discordapp.net/attachments/1385036679756386395/1385037659122040882/charizard-gmax6.png?ex=6899d316&is=68988196&hm=9332e84c2bf8fd31293810f6b9dd13a8118bc9f161725ce8c1ce467971d16e9d&=&format=webp&quality=lossless&width=36&height=34"
    coa = "https://media.discordapp.net/attachments/1385036679756386395/1385109469062631545/coalossal-gmax6.png?ex=68996d37&is=68981bb7&hm=0a2e5027321592dca028d834a55428595d980041a8d588fee0e61102e5785aab&=&format=webp&quality=lossless&width=42&height=50"
    cin = "https://media.discordapp.net/attachments/1385036679756386395/1385056247002431642/cinderace-gmax6.png?ex=6899e466&is=689892e6&hm=23eec655343c7c50943aef37acea0069323fe4cb428262f028679ca6c7fe7acc&=&format=webp&quality=lossless&width=42&height=50"
    cop = "https://media.discordapp.net/attachments/1385036679756386395/1385111621851938866/copperajah-gmax6.png?ex=68996f38&is=68981db8&hm=0bf3824ff736cb74c784e57700ccdc7dcc1fd598fd8e1727d9c8ed1f1bb39e98&=&format=webp&quality=lossless&width=36&height=50"
    cor = "https://media.discordapp.net/attachments/1385036679756386395/1385219173633888310/corviknight-gmax6.png?ex=6899d363&is=689881e3&hm=35bd6695380d500a3759c2e31868cb5f91ce24dea1251ed7f395cb773a0de14a&=&format=webp&quality=lossless&width=50&height=45"
    dre = "https://media.discordapp.net/attachments/1385036679756386395/1385061753658019901/drednaw-gmax6.png?ex=6899e987&is=68989807&hm=c8324e844bf58852087e95acff358cafd1c83958dc1bab6bded47fa1b84c64ea&=&format=webp&quality=lossless&width=25&height=28"
    dur = "https://media.discordapp.net/attachments/1385036679756386395/1385062909779902514/duraludon-gmax6.png?ex=6899ea9a&is=6898991a&hm=66e8b69732fa38fbfe96c26bd63d43da30c86c2115d49de406af7cb75f24b825&=&format=webp&quality=lossless&width=39&height=50"
    eet = "https://media.discordapp.net/attachments/1385036679756386395/1385064802837069834/1334652885211938909.png?ex=6899ec5e&is=68989ade&hm=84f029929ed25c609a5f721c5017d990d6b57ce9620aded2ebbc1ccf41b4a0cf&=&format=webp&quality=lossless&width=64&height=70"
    eev = "https://media.discordapp.net/attachments/1385036679756386395/1385066374753161287/eevee-gmax6.png?ex=6899edd5&is=68989c55&hm=5ec476f045874d6dc9b6ceeef551ac586b7525f7aba5ae61a14f6d3375179152&=&format=webp&quality=lossless&width=25&height=26"
    fla = "https://media.discordapp.net/attachments/1385036679756386395/1385105706058780743/flapple-gmax6.png?ex=689969b6&is=68981836&hm=d06c07e53e9b130b08ff724b7158b84955ee549b41b5f62160f1b8430bbfa19d&=&format=webp&quality=lossless&width=29&height=33"
    gar = "https://media.discordapp.net/attachments/1385036679756386395/1385067492942020758/garbodor-gmax6.png?ex=6899eedf&is=68989d5f&hm=862df55e141c4fbf13bcc1c3708e63a6bd1350763a8eed6c0f5868c26f6bd863&=&format=webp&quality=lossless&width=36&height=30"
    gen = "https://media.discordapp.net/attachments/1385036679756386395/1385069242847723631/gengar-gmax6.png?ex=689947c0&is=6897f640&hm=657241521a0b0ce0a3d57f1836cdf11fe29721785fddaa67ec878f998d29d0d0&=&format=webp&quality=lossless&width=35&height=26"
    gri = "https://media.discordapp.net/attachments/1385036679756386395/1385221572247162941/grimmsnarl-gmax6.png?ex=6899d59e&is=6898841e&hm=03229ca8f58f6b0fcd8013caf83f2e18f072ad22b82765a5d3de028c51aa1ce1&=&format=webp&quality=lossless&width=34&height=50"
    hat = "https://media.discordapp.net/attachments/1385036679756386395/1385222607842050109/hatterene-gmax6.png?ex=6899d695&is=68988515&hm=377bf45b7b606c7b2c97e8ff8cd9fe267c916b10e2a5616763085e0dd4a75c0e&=&format=webp&quality=lossless&width=32&height=50"
    int = "https://media.discordapp.net/attachments/1385036679756386395/1385070107457228860/inteleon-gmax3.png?ex=6899488e&is=6897f70e&hm=375db2b8d2457a430eac7abb5fb83c0c25db9c995173238e03da491b0510c003&=&format=webp&quality=lossless&width=23&height=50"
    kin = "https://media.discordapp.net/attachments/1385036679756386395/1385071582040293376/kingler-gmax6.png?ex=689949ee&is=6897f86e&hm=10298fa15c5324d223a304fba76f3b06bcefc6e29fc9ae4f3f125ebb2de0feab&=&format=webp&quality=lossless&width=34&height=34"
    lap = "https://media.discordapp.net/attachments/1385036679756386395/1385074278294229112/lapras-gmax6.png?ex=68994c71&is=6897faf1&hm=21a5869a9b9d186c6a8d294ef2a5e789cdc5fb1b7ea413538d0e8fd6f4bd6046&=&format=webp&quality=lossless&width=28&height=27"
    mac = "https://media.discordapp.net/attachments/1385036679756386395/1385075611088977990/machamp-gmax6.png?ex=68994daf&is=6897fc2f&hm=786d7ed0d5eb55efec4aca2ef6a6b4c382a281b4a03e4aa9e6306c651bc91830&=&format=webp&quality=lossless&width=30&height=30"
    mel = "https://media.discordapp.net/attachments/1385036679756386395/1385112512915046410/melmetal-gmax6.png?ex=6899700d&is=68981e8d&hm=8a3d92e746a35e4f838764dfc6c1b82482fb2ce50605ceaaa3dfe9b77785a70a&=&format=webp&quality=lossless&width=50&height=42"
    meo = "https://media.discordapp.net/attachments/1385036679756386395/1385095178796142603/meowth-gmax6.png?ex=68995fe8&is=68980e68&hm=70d76330c58c218b24530ccb4ae04f4d2e27658f09e4ccb97a06ba2db166f856&=&format=webp&quality=lossless&width=25&height=34"
    orb = "https://media.discordapp.net/attachments/1385036679756386395/1385224693455392828/orbeetle-gmax6.png?ex=6899d887&is=68988707&hm=ef54ab5a6cd21a29adcf1ef88101117a4c54930910f094d8869378ea14a543be&=&format=webp&quality=lossless&width=44&height=36"
    pik = "https://media.discordapp.net/attachments/1385036679756386395/1385095817320333503/pikachu-gmax6.png?ex=68996080&is=68980f00&hm=70be73c122b7cef74ab25f67a2e0355ad9519724dc3a57fd5f16297e651cf169&=&format=webp&quality=lossless&width=23&height=28"
    ril = "https://media.discordapp.net/attachments/1385036679756386395/1385096760594137200/rillaboom-gmax6.png?ex=68996161&is=68980fe1&hm=21a50364f5219e7c482c70dfc74319c665e249e87af37efb4e3f249945dfdfcb&=&format=webp&quality=lossless&width=50&height=41"
    san = "https://media.discordapp.net/attachments/1385036679756386395/1385097621554729070/sandaconda-gmax6.png?ex=6899622e&is=689810ae&hm=71a2caf7d8721baf48887b96ce22675bba01b1b053071ed3a5a06244b20e56a9&=&format=webp&quality=lossless&width=37&height=41"
    sno = "https://media.discordapp.net/attachments/1385036679756386395/1385098532221882500/snorlax-gmax6.png?ex=68996307&is=68981187&hm=d3317919ce42cc53dbcc3a593bdda15e8da3cb95c175c8a79a42f21581a27545&=&format=webp&quality=lossless&width=35&height=33"
    tox = "https://media.discordapp.net/attachments/1385036679756386395/1385099620157231134/toxtricity-gmax6.png?ex=6899640b&is=6898128b&hm=7520d941fb2025478c5c1043e84bb1d76c1fc8ba45023164349f7b558ba0c29a&=&format=webp&quality=lossless&width=36&height=41"
    urs = "https://media.discordapp.net/attachments/1385036679756386395/1385100586629726269/urshifu-rapid-strike-gmax6.png?ex=689964f1&is=68981371&hm=c30b3d5c96e151829806c655e2dbb7178f81d9e45101a8fa9990e085c3b7ff62&=&format=webp&quality=lossless&width=44&height=50"
    uss = "https://media.discordapp.net/attachments/1385036679756386395/1385223454046949437/urshifu-gmax6.png?ex=6899d75f&is=689885df&hm=29661acc58cd4ee3d941a2fcad62a8d965118e497f8515f8ae2dfd385683c972&=&format=webp&quality=lossless&width=42&height=50"
    ven = "https://media.discordapp.net/attachments/1385036679756386395/1385101165355864134/venusaur-gmax6.png?ex=6899657b&is=689813fb&hm=72be465c1247e82876c366a2ab03d0196a0b5a8e616571b4d3f6b8ce3aad44e5&=&format=webp&quality=lossless&width=33&height=34"

class WB_REGEMOJI:
    alc = "<:alcremiegmax3:1416912840844902441>"
    app = "<:flapplegmax3:1416912454172282920>"
    bla = "<:blastoisegmax3:1416909236876873952>"
    but = "<:butterfreegmax3:1416912349478260838>"
    cen = "<:centiskorchgmax3:1416909723005091880>"
    cha = "<:charizardgmax3:1416909152562712661>"
    coa = "<:coalossalgmax3:1416912816937635860>"
    cin = "<:cinderacegmax3:1416909673025634356>"
    cop = "<:copperajahgmax3:1416912615891800125>"
    cor = "<:corviknightgmax3:1416912688814227488>"
    dre = "<:drednawgmax3:1416909740373577768>"
    dur = "<:duraludongmax3:1416909770459316264>"
    eet = "<:eternamaxeternatus:1416909834355343422>"
    eev = "<:eeveegmax3:1416910393653334116>"
    fla = "<:flapplegmax3:1416912454172282920>"
    gar = "<:garbodorgmax3:1416910415581151352>"
    gen = "<:gengargmax3:1416910547424641154>"
    gri = "<:grimmsnarlgmax3:1416912543343181884>"
    hat = "<:hatterenegmax3:1416912186151927819>"
    int = "<:inteleongmax3:1416910623199068283>"
    kin = "<:kinglergmax3:1416910872969871461>"
    lap = "<:laprasgmax3:1416910962342232145>"
    mac = "<:machampgmax3:1416910991345717328>"
    mel = "<:melmetalgmax3:1416912268871860255>"
    meo = "<:meowthgmax3:1416911177664958464>"
    orb = "<:orbeetlegmax3:1416912110402801715>"
    pik = "<:pikachugmax3:1416911253422608394>"
    ril = "<:rillaboomgmax3:1416911332447490179>"
    san = "<:sandacondagmax3:1416911432095629452>"
    sno = "<:snorlaxgmax3:1416911520432132219>"
    tox = "<:toxtricitygmax3:1416911608701255730>"
    urs = "<:urshifurapidstrikegmax3:1416911721892806819>"
    uss = "<:urshifugmax3:1416911899840479332>"
    ven = "<:venusaurgmax3:1416911965737058374>"

class WB_SHINYEMOJI:
    alc = "<:alcremiegmax6:1416912853751038063>"
    app = "<:flapplegmax6:1416912465219817492>"
    bla = "<:blastoisegmax6:1416909257764245605>"
    but = "<:butterfreegmax6:1416912365215154359>"
    cen = "<:centiskorchgmax6:1416909707951472750>"
    cha = "<:charizardgmax3:1416909152562712661>"
    coa = "<:coalossalgmax6:1416912829016969276>"
    cin = "<:cinderacegmax6:1416909684148797551>"
    cop = "<:copperajahgmax6:1416912632014704690>"
    cor = "<:corviknightgmax6:1416912700222734357>"
    dre = "<:drednawgmax6:1416909754109788210>"
    dur = "<:duraludongmax6:1416909790470471690>"
    eet = "<:shinyeternamax:1416909845952466964>"
    eev = "<:eeveegmax6:1416910402733871125>"
    fla = "<:flapplegmax6:1416912465219817492>"
    gar = "<:garbodorgmax6:1416910430915395664>"
    gen = "<:gengargmax6:1416910560762662963>"
    gri = "<:grimmsnarlgmax6:1416912555133370480>"
    hat = "<:hatterenegmax6:1416912175188017152>"
    int = "<:inteleongmax6:1416910607323758666>"
    kin = "<:kinglergmax6:1416910887163269241>"
    lap = "<:laprasgmax6:1416910974711107584>"
    mac = "<:machampgmax6:1416911003303546921>"
    mel = "<:melmetalgmax6:1416912284030205982>"
    meo = "<:meowthgmax6:1416911192538222673>"
    orb = "<:orbeetlegmax6:1416912124306788433>"
    pik = "<:pikachugmax6:1416911267179921549>"
    ril = "<:rillaboomgmax6:1416911347140001962>"
    san = "<:sandacondagmax6:1416911458335199232>"
    sno = "<:snorlaxgmax6:1416911535753658409>"
    tox = "<:toxtricitygmax6:1416911625310568579>"
    urs = "<:urshifurapidstrikegmax6:1416911745116540968>"
    uss = "<:urshifugmax3:1416911899840479332>"
    ven = "<:venusaurgmax6:1416911980161269861>"

class WB_ConsitentStrat:
    gri = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento`
EVs: `HP 252` `SPD 252`

- **Mega Gardevoir**
Equip: `Metronome` | `Fairy Feather` | `Expert Belt`
Moves: `Moonblast` `Calm Mind` ` Draining Kiss`
EVs: `SPA 252` `SPD 252` `HP 6`

**STRATEGY:**
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Acid Spray` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **Mega Gardevoir** use `Calm Mind` 6x.
- After the set-up above, spam `Moonblast`
- Use `Draining Kiss` to heal."""

    uss = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento`
EVs: `HP 252` `SPD 252`

- **Mega Gardevoir**
Equip: `Metronome`
Moves: `Moonblast` `Draining Kiss` `Calm Mind`
EVs: `SPA 252` `SPD 252` `HP 6`

**STRATEGY:**
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Acid Spray` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **Mega Gardevoir** use `Calm Mind` 6x times.
- After the set-up above, spam `Moonblast`.
- Use `Draining Kiss` to heal."""

    mewtwo_strat = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento`
EVs: `HP 252` `SPD 252`

- **Mega Mewtwo Y**
Equip: `Metronome`
Moves: `Stored Power` `Recover` `Calm Mind` `Bulk Up`
EVs: `SPA 252` `SPD 252` `HP 6`

**STRATEGY:**
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Acid Spray` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **MMY** use `Calm Mind` 6x then `Bulk Up` atleast once. The amount of `Bulk Ups` may change depending on how many people participate and how fast the boss dies.
- After the set-up above, spam `Stored Power`
- Use `Recover` to heal."""


class WB_MVPStrat:
    gri = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Screech` `Memento`
EVs: `HP 252` `SPD 252`

- **Zacian-Crowned**
Equip: `Metronome`
Moves: `Behemoth Blade` `Sword Dance`
EVs: `ATK 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6 defense, then use 1x `Memento`.
- With **Zacian-Crowned** use `Sword Dance` 3x.
- After the set-up above, spam `Behemoth Blade`
- Use `Max Potions` to heal."""

    uss = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento`
EVs: `HP 252` `SPD 252`

- **Gmax Hatterene**
Equip: `Metronome`
Moves: `Gmax Smite` `Draining Kiss` `Calm Mind`
EVs: `SPA 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Acid Spray` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **GMAX Hatterene** use `Calm Mind` 6x times.
- After the set-up above, spam `Gmax Smite`.
- Use `Draining Kiss` to heal."""

    alc = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento` `Screech`
EVs: `HP 252` `SPD 252`

- **Zacian-Crowned**
Equip: `Metronome`
Moves: `Behemoth Blade` `Sword Dance`
EVs: `ATK 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **Zacian-Crowned** use `Sword Dance` 3x.
- After the set-up above, spam `Behemoth Blade`
- Use `Max Potions` to heal."""

    app_fla = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento`
EVs: `HP 252` `SPD 252`

- **Golden Kyurem-White**
Equip: `Choice Cloak` | `Choice Specs` | `Expert Belt` | `Metronome`
Moves:  `Ice burn` `Roost`
EVs: `SPA 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- Must have 3x `Aux Powerguard`
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Acid Spray` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **GKW** use 3x `Aux Powerguard` in order to max ATK, SPA, DEF, & SPD.
- After the boost above, spam `Ice Burn`.
- Use `Roost` to heal.
- You can run `Choice Specs` instead of `Metronome` and heal using `Max Potions` instead of `Recover` - if you have alot of `Max Potions`."""

    but = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Screech` `Memento`
EVs: `HP 252` `SPD 252`

- **Golden Rhyperior**
Equip: `Metronome` | `Choice Band`
Moves: `Rock Wrecker` `Swords Dance`
EVs: `ATK 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- Must have 3x `Aux Powerguard`
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6 defense, then use 1x `Memento`.
- With **Golden Rhyperior** use 3x `Aux Powerguard` in order to max ATK, SPA, DEF, & SPD.
- After the boost above, spam `Rock Wrecker`.
- Use `Max Potions` to heal."""

    coa = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento`
EVs: `HP 252` `SPD 252`

- *Gmax Inteleon**
Equip: `Metronome` | `Choice Specs` | `Expert Belt` | `Choice Cloak`
Moves: `Max Geyser`  `Max Quake` `Max Futterby` `Gmax Hydrosnipe`
EVs: `SPA 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- Must have 3x `Aux Powerguard`
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Acid Spray` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **Gmax Inteleon** use 3x `Aux Powerguard` in order to max ATK, SPA, DEF, & SPD.
- After the boost above, use `Max Geyser` to get **Rain** while dealing damage.
- Spam `Gmax Hydrosnipe`, and use `Max Geyser` again whenever **Rain** stops.
- Use `Max Potions` to heal.
- If you use any `Choice Items`, just spam `Max Geyser`."""

    cop = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Screech` `Memento`
EVs: `HP 252` `SPD 252`

- **Pangoro**
Equip: `Metronome` | `Black Glasses` | `Choice Band` | `Choice Cloak`
Moves: `Stored Power` `Recover` `Calm Mind` `Bulk Up`
EVs: `ATK 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- Must have 3x `Aux Powerguard`
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6 defense, then use 1x `Memento`.
- With **Pangoro** use 3x `Aux Powerguard` in order to max ATK, SPA, DEF, & SPD.
- After the boost above, spam `Power Trip`.
- Use `Max Potions` to heal."""
    cor = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento` `Screech`
EVs: `HP 252` `SPD 252`

- **Pangoro**
Equip: `Metronome` | `Black Glasses` | `Choice Band` | `Choice Cloak`
Moves: `Power Trip` `Bulk Up`
EVs: `ATK 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- Must have 5x `Aux Powerguard`
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6 defense, then use 1x `Memento`.
- With **Pangoro** use 3x `Aux Powerguard` in order to max ATK, SPA, DEF, & SPD.
- After the boost above, spam `Power Trip`.
- Use `Max Potions` to heal."""
    hat = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Screech` `Memento`
EVs: `HP 252` `SPD 252`

- **Zacian-Crowned**
Equip: `Metronome`
Moves: `Behemoth Blade` `Sword Dance`
EVs: `ATK 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Screech` 3x times to get -6 defense, then use 1x `Memento`.
- With **Zacian-Crowned** use `Sword Dance` 3x.
- After the set-up above, spam `Behemoth Blade`
- Use `Max Potions` to heal."""

    mel = f"""**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento`
EVs: `HP 252` `SPD 252`

- **Gmax Charizard**
Equip: `Choice Specs` | `Expert Belt` | `Choice Cloak` | `Metronome`
Moves: `Stored Power` `Recover` `Calm Mind` `Bulk Up`
EVs: `SPA 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- Must have 3x `Aux Powerguard`
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Acid Spray` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **Gmax Charizard** use 3x `Aux Powerguard` in order to max ATK, SPA, DEF, & SPD.
- After the boost above, spam `Max Flare`.
- Use `Roost` to heal.
- You can run `Choice Specs` instead of `Metronome` and heal using `Max Potions` instead of `Recover` - if you have alot of `Max Potions`."""
    mewtwo = """**TEAM:**
- **Grimer**
Equip: NA
Moves: `Memento`
EVs: -

- **Muk**
Equip: `Loaded Dice`
Moves: `Acid Spray` `Memento`
EVs: `HP 252` `SPD 252`

- **Mega Mewtwo Y**
Equip: `Metronome`
Moves: `Stored Power` `Recover` `Agility` `Double Team`
EVs: `SPA 252` `SPD 252` `HP 6`

**MVP STRATEGY:** 🌟
- Must have 3x `Aux Powerguard`
- **Grimer** can be used at lvl 1. Use `Memento` first turn.
- With **Muk**, use `Acid Spray` 3x times to get -6 sp defense, then use 1x `Memento`.
- With **MMY** use 3x `Aux Powerguard` in order to max ATK, SPA, DEF, & SPD.
- Use Agility/Double Team depending on how fast the boss dies.
- For Fast Boss, 3x Agility
- For Long Boss, 3x Agility, and 6x Double Team
- After the boost above, spam `Stored Power`.
- Use `Recover` to heal.
- You can run `Choice Specs` instead of `Metronome` and heal using `Max Potions` instead of `Recover` - if you have alot of `Max Potions`."""
