; RAW data debt. Bootstrap: tools/datagen.py; edit this source thereafter.
.286
; Menu option/string offset table at DGROUP:00DA..00EC.
; GAME:0652 indexes the option entries and copies the selected DS string.
extrn ext_013B:far
_DATA segment word public 'DATA'
public ext_5C09
ext_5C09 label far
    db 000h, 000h, 000h, 000h, 000h, 067h, 045h
    dw seg ext_013B ; image 05C129
    db 000h, 000h
    dw seg ext_0A67 ; image 05C12D
    db 04Ch, 026h
    dw seg ext_5C09 ; image 05C131
    db 000h, 000h
    dw seg ext_1A38 ; image 05C135
    db 030h, 001h, 000h, 0A0h, 081h, 046h
    dw seg ext_013B ; image 05C13D
    db 081h, 049h
    dw seg ext_013B ; image 05C141
    db 000h, 000h
    dw seg ext_2BC6 ; image 05C145
    db 048h, 026h
    dw seg ext_5C09 ; image 05C149
    db 000h, 000h, 00Ah, 064h, 0E8h, 003h, 010h, 027h, 060h, 000h, 0BCh, 002h, 015h
    db 14 dup (000h)
    db 0FFh, 0FFh, 0FFh, 0FFh
    dw offset dg_text_0BCB
    dw offset dg_text_0BD2
    dw offset dg_text_0BD9
    dw offset dg_text_0BE0
    dw offset dg_text_0BEB
    dw offset dg_text_0BAA
    dw offset dg_text_0BB5
    dw offset dg_text_0BC0
    dw offset dg_text_00EE
    dw offset dg_text_0492
dg_text_00EE label byte
    db 'CAVITY'
    db 000h
    db 'FIRSTCOMMUNION'
    db 000h
    db 'FIGURATIVETHEATRE'
    db 000h
    db 'BURNTOFFERINGS'
    db 000h
    db 'MYSTERIUMINQUITATIS'
    db 000h
    db 'DREAMFORMOTHER'
    db 000h
    db 'UNCERTAINJOURNEY'
    db 000h
    db 'SPIRITUALCRAMP'
    db 000h
    db 'ROMEOSDISTRESS'
    db 000h
    db 'RESURRECTION'
    db 000h
    db 'PRAYER'
    db 000h
    db 'DEATHWISH'
    db 000h
    db 'DOGS'
    db 000h
    db 'DESPERATEHELL'
    db 000h
    db 'AWAKEATTHEWALL'
    db 000h
    db 'SLEEPWALK'
    db 000h
    db 'THEDROWNING'
    db 000h
    db 'THEBLUEHOUR'
    db 000h
    db 'ASEVENINGFALLS'
    db 000h
    db 'ANDROGYNOUSNOISE'
    db 000h
    db 'HANDPERMEATES'
    db 000h
    db 'ELECTRADESCENDING'
    db 000h
    db 'CERVIXCOUCH'
    db 000h
    db 'THISGLASSHOUSE'
    db 000h
    db 'FLEEINGSOMNAMBULIST'
    db 000h
    db 'THESOMNOLENTPERSUIT'
    db 000h
    db 'ASHES'
    db 000h
    db 'ASHESPARTII'
    db 000h
    db 'WHENIWASBED'
    db 000h
    db 'LAMENTOVERTHESHADOWS'
    db 000h
    db 'FACE'
    db 000h
    db 'THELUXURYOFTEARS'
    db 000h
    db 'OFTHEWOUND'
    db 000h
    db 'BELIEVERSOFTHEUNPURE'
    db 000h
    db 'OUVERTURE'
    db 000h
    db 'WINDKISSEDPICTURES'
    db 000h
    db 'THELAKEOFFIRE'
    db 000h
    db 'BLASTOFTHEBOUGH'
    db 000h
    db 'AMATERASU'
    db 000h
    db 'THEABSOLUTE'
    db 000h
    db 'LACRIMACHRISTI'
    db 000h
    db 'BETWEENYOUTH'
    db 000h
    db 'AFTERTHERAIN'
    db 000h
    db 'WILLOTHEWISP'
    db 000h
    db 'TALESOFINNOCENCE'
    db 000h
    db 'STRAPPINGMEDOWN'
    db 000h
    db 'THEDANZIGWALTZ'
    db 000h
    db 'CHIMEREDESIDELA'
    db 000h
    db 'SILENTTHUNDER'
    db 000h
    db 'STRANGEFORTUNE'
    db 000h
    db 'VENTRILOQUIST'
    db 000h
    db 'GLOOMYSUNDAY'
    db 000h
    db 'THEDEATHOFJOSEF'
    db 000h
    db 'SONGOFSOLOMON'
    db 000h
    db 'SICKOFLOVE'
    db 000h
    db 'VANITY'
    db 000h
    db 'FOURHORSEMEN'
    db 000h
    db '1983'
    db 000h
    db 'OMEGADAWN'
    db 000h
    db 'ARINGINGINTHEIREARS'
    db 000h
    db 'THEGOLDENAGE'
    db 000h
    db 'ALPHASUNSET'
    db 000h
    db 'SPILTBLOOD'
    db 000h
    db 'RAWWAR'
    db 000h
    db 'REFLECTIONS'
    db 000h
    db 'CHURCHOFNORETURN'
    db 000h
    db 'WHATSTHEVERDICT'
    db 000h
    db 'ZEROSEX'
    db 000h
    db 'THISISHERESY'
    db 000h, 0FFh
dg_text_0492 label byte
    db 'ALONEINTOTHEALONE'
    db 000h
    db 'ONLYSHADOWSOFHOOKS'
    db 000h
    db 'CHRISTSFIRSTHOWLING'
    db 000h
    db 'FIELDSOFRAPE'
    db 000h
    db 'GREATBLACKTIME'
    db 000h
    db 'MALDORORESTMORT'
    db 000h
    db 'ADAYINDOGLAND'
    db 000h
    db 'EXTRAECCLASIAM'
    db 000h
    db 'NULLASALUS'
    db 000h
    db 'THESHELLSHAVECRACKED'
    db 000h
    db 'FROMBROKENCROSS'
    db 000h
    db 'STPETERSKEYALLBLOODY'
    db 000h
    db 'BENEDICTION'
    db 000h
    db 'BLESSING'
    db 000h
    db 'NORTH'
    db 000h
    db 'BLACKSUNBLOODYMOON'
    db 000h
    db 'OHCOALBLACKSMITH'
    db 000h
    db 'PANZERRUNE'
    db 000h
    db 'BLACKFLOWERSPLEASE'
    db 000h
    db 'THEFINALCHURCH'
    db 000h
    db 'THESUMMEROFLOVE'
    db 000h
    db 'HEYHOTHENODDYOH'
    db 000h
    db 'BEAUSOLEIL'
    db 000h
    db 'SCARLETWOMAN'
    db 000h
    db 'THESTAIRSONG'
    db 000h
    db 'HULLOANGEL'
    db 000h
    db 'SINCEYESTERDAY'
    db 000h
    db 'VALEDICTION'
    db 000h
    db 'MALEDICTION'
    db 000h
    db 'DOGUN'
    db 000h
    db 'FOREVERCHANGING'
    db 000h
    db 'THEBALLADOF'
    db 000h
    db 'THEPALECHRIST'
    db 000h
    db 'CHRISTANDTHE'
    db 000h
    db 'PALEQUEENS'
    db 000h
    db 'MIGHTYINSORROW'
    db 000h
    db 'THEREDFACEOFGOD'
    db 000h
    db 'THEBREATHAND'
    db 000h
    db 'PAINOFGOD'
    db 000h
    db 'THATSALLFOLKS'
    db 000h
    db 'HAPPYBIRTHDAY'
    db 000h
    db 'THEBIRDSHAVE'
    db 000h
    db 'STOPPEDSINGING'
    db 000h
    db 'KHORBAINYESDMIGS'
    db 000h
    db 'LAMENTFORHER'
    db 000h
    db 'THEDEATHOFTHECORN'
    db 000h
    db 'ASONGFORDOUGLAS'
    db 000h
    db 'AFTERHESDEAD'
    db 000h
    db 'TERRATEGITTERRAM'
    db 000h, 042h, 045h, 000h
    db 'HOOVES'
    db 000h
    db 'HORSEY'
    db 000h
    db 'THEYRETURNEDTO'
    db 000h
    db 'THEIREARTH'
    db 000h
    db 'FALLING'
    db 000h
    db 'THEDREAMOFASHADOW'
    db 000h
    db 'OFSMOKE'
    db 000h
    db 'PASSINGHORSES'
    db 000h
    db 'ANYWAYPEOPLEDIE'
    db 000h
    db 'TOBLACKENEDEARTH'
    db 000h
    db 'OHMERRYGOROUND'
    db 000h
    db 'CROWLEYMASSUNVEILED'
    db 000h
    db 'PAPERBACKHONEY'
    db 000h
    db 'THEFALLOF'
    db 000h
    db 'CHRISTOPHERROBIN'
    db 000h
    db 'ABEGINNING'
    db 000h
    db 'THEDESCENTOFLONG'
    db 000h
    db 'SATANANDBABYLON'
    db 000h
    db 'ASADNESSSONG'
    db 000h
    db 'INTHEHEARTOFTHEWOOD'
    db 000h
    db 'ANDWHATIFOUNDTHERE'
    db 000h
    db 'MARYWAITSINSILENCE'
    db 000h
    db 'ASILENCESONG'
    db 000h
    db 'ALAMENTFORMYSUZANNE'
    db 000h
    db 'RIVERDEADBANK'
    db 000h
    db 'ALLTHESTARSAREDEAD'
    db 000h
    db 'ROSYSTARTEARS'
    db 000h
    db 'FROMHEAVEN'
    db 000h
    db 'WHENTHEMAYRAINCOMES'
    db 000h
    db 'THUNDERPERFECTMIND'
    db 000h
    db 'ASADSADNESSSONG'
    db 000h, 0FFh, 0FEh
    db 'PROGRAMMED'
    db 00Dh, 0FEh, 042h, 059h, 00Dh, 0FEh
    db 'MARIO KNEZOVIC'
    db 00Dh, 0FEh
    db 'WITH'
    db 00Dh, 0FEh
    db 'CARSTEN NEUBAUER'
    db 000h, 0FEh
    db 'INTROS CODED'
    db 00Dh, 0FEh, 042h, 059h, 00Dh, 0FEh
    db 'MARIO KNEZOVIC'
    db 00Dh, 0FEh
    db 'WITH'
    db 00Dh, 0FEh
    db 'CLAUDIA SCHOLZ'
    db 000h, 0FEh
    db 'ORIGINAL'
    db 00Dh, 0FEh
    db 'AMIGA VERSION'
    db 00Dh, 0FEh
    db 'PROGRAMMED'
    db 00Dh, 0FEh, 042h, 059h, 00Dh, 0FEh
    db 'THOMAS KLINGER'
    db 00Dh, 0FEh, 041h, 04Eh, 044h, 00Dh, 0FEh, 042h, 04Ah, 099h
    db 'RN ROY'
    db 000h, 0FEh
    db 'ORIGINAL'
    db 00Dh, 0FEh
    db 'AMIGA GRAPHICS'
    db 00Dh, 0FEh
    db 'DRAWN'
    db 00Dh, 0FEh, 042h, 059h, 00Dh, 0FEh
    db 'THOMAS KLINGER'
    db 000h, 0FEh
    db 'PC GRAPHICS'
    db 00Dh, 0FEh, 042h, 059h, 00Dh, 0FEh
    db 'MICHAEL DETERT'
    db 00Dh, 0FEh
    db 'WITH'
    db 00Dh, 0FEh
    db 'CARSTEN NEUBAUER'
    db 00Dh, 0FEh
    db 'MARIO KNEZOVIC'
    db 000h, 0FEh
    db 'MUSIC AND FX'
    db 00Dh, 0FEh, 042h, 059h, 00Dh, 0FEh
    db 'HAIKO RUTTMANN'
    db 000h, 0FEh
    db 'LEVELS'
    db 00Dh, 0FEh
    db 'DESIGNED'
    db 00Dh, 0FEh, 042h, 059h, 00Dh, 0FEh
    db 'PETER SCHMITZ'
    db 00Dh, 0FEh, 041h, 04Eh, 044h, 00Dh, 0FEh, 042h, 04Ah, 099h
    db 'RN ROY'
    db 000h, 0FEh
    db 'SPECIAL THANKS'
    db 00Dh, 0FEh, 054h, 04Fh, 00Dh, 0FEh
    db 'THOMAS DETERT'
    db 00Dh, 0FEh, 041h, 04Eh, 044h, 00Dh, 0FEh
    db 'OLIVER K'
    db 099h, 04Eh, 049h, 047h, 000h, 0FFh
    db ' F1: START GAME'
    db 00Dh
    db ' F2: ENTER PASSWORD'
    db 00Dh
    db ' F3: BOPA! '
    db 00Dh
    db ' F4: BONES PARK'
    db 00Dh
    db ' F5: CONTROL OPTIONS'
    db 00Dh, 0FDh
    db 'PASSWORD:          '
    db 00Dh
    db 'NONE                '
    db 000h, 0FFh
    db 'PLAYER 1:'
    db 00Dh
    db ' F1: BONES PARK'
    db 00Dh
    db 'PLAYER 2:'
    db 00Dh
    db ' F2: BONES PARK'
    db 00Dh, 00Dh, 00Dh
    db 'ESC: MAIN MENU'
    db 000h, 0FFh
dg_text_0BAA label byte
    db 'KEYBOARD  '
    db 000h
dg_text_0BB5 label byte
    db 'JOYSTICK A'
    db 000h
dg_text_0BC0 label byte
    db 'JOYSTICK B'
    db 000h
dg_text_0BCB label byte
    db 'EASY  '
    db 000h
dg_text_0BD2 label byte
    db 'MEDIUM'
    db 000h
dg_text_0BD9 label byte
    db 'HARD  '
    db 000h
dg_text_0BE0 label byte
    db 'ONE PLAYER'
    db 000h
dg_text_0BEB label byte
    db 'TEAM MODE '
    db 000h, 0FEh
    db 'LEVEL 00'
    db 000h, 0FEh
    db 'PASSWORD:'
    db 00Dh, 000h, 0FEh
    db 'BAD LUCK'
    db 00Dh, 0FEh
    db 'YOU FAILED'
    db 00Dh, 000h, 0FEh
    db 'CONGRATULATIONS'
    db 00Dh, 0FEh
    db 'YOU ARE ONE OF THE'
    db 00Dh, 0FEh
    db 'FIVE BEST CABBIES'
    db 00Dh, 00Dh
    db 'ENTER YOUR NAME:'
    db 00Dh
    db 12 dup (020h)
    db 000h, 0FFh, 0FEh
    db 'TOP FIVE'
    db 00Dh, 0FDh
    db 'FRED           20000'
    db 00Dh
    db 'BARNEY         10000'
    db 00Dh
    db 'WILMA           5000'
    db 00Dh
    db 'PEBBLES         2500'
    db 00Dh
    db 'KALKI           1000'
    db 00Dh, 000h, 0FFh
    db 'UGH!.HI'
    db 000h, 000h, 0DAh, 000h, 0E0h, 000h, 0E6h, 000h, 0EAh, 000h, 0EBh, 000h, 0ECh, 000h, 0EDh, 000h
    db 0EEh, 000h, 0EFh, 000h, 0F0h, 000h, 0F1h, 000h, 0F2h, 000h, 0F3h, 000h, 0F4h, 000h, 0F5h, 000h
    db 0FFh, 0FFh, 0F6h, 000h, 0F7h, 000h, 0F8h, 000h, 0F9h, 000h, 0FAh, 000h, 0FBh, 000h, 0FCh, 000h
    db 0FDh, 000h, 0FEh, 000h, 0FFh, 000h, 000h, 001h, 001h, 001h, 0FFh, 0FFh, 0EAh, 000h, 0FFh, 0FFh
    db 0F6h, 000h, 0FFh, 0FFh, 02Fh, 002h, 030h, 002h, 031h, 002h, 032h, 002h, 033h, 002h, 034h, 002h
    db 0FFh, 0FFh, 035h, 002h, 036h, 002h, 037h, 002h, 038h, 002h, 039h, 002h, 03Ah, 002h, 0FFh, 0FFh
    db 023h, 002h, 024h, 002h, 025h, 002h, 026h, 002h, 027h, 002h, 028h, 002h, 0FFh, 0FFh, 029h, 002h
    db 02Ah, 002h, 02Bh, 002h, 02Ch, 002h, 02Dh, 002h, 02Eh, 002h, 0FFh, 0FFh, 053h, 002h, 053h, 002h
    db 053h, 002h, 053h, 002h, 053h, 002h, 053h, 002h, 0FFh, 0FFh, 054h, 002h, 054h, 002h, 054h, 002h
    db 054h, 002h, 054h, 002h, 054h, 002h, 0FFh, 0FFh, 047h, 002h, 048h, 002h, 049h, 002h, 04Ah, 002h
    db 04Bh, 002h, 04Ch, 002h, 0FFh, 0FFh, 04Dh, 002h, 04Eh, 002h, 04Fh, 002h, 050h, 002h, 051h, 002h
    db 052h, 002h, 0FFh, 0FFh, 055h, 002h, 055h, 002h, 055h, 002h, 055h, 002h, 055h, 002h, 055h, 002h
    db 0FFh, 0FFh, 056h, 002h, 056h, 002h, 056h, 002h, 056h, 002h, 056h, 002h, 056h, 002h, 0FFh, 0FFh
    db 03Bh, 002h, 03Ch, 002h, 03Dh, 002h, 03Eh, 002h, 03Fh, 002h, 040h, 002h, 0FFh, 0FFh, 041h, 002h
    db 042h, 002h, 043h, 002h, 044h, 002h, 045h, 002h, 046h, 002h, 0FFh, 0FFh, 013h, 001h, 014h, 001h
    db 015h, 001h, 016h, 001h, 017h, 001h, 018h, 001h, 019h, 001h, 01Ah, 001h, 01Bh, 001h, 01Ch, 001h
    db 0FFh, 0FFh, 013h, 001h, 0FFh, 0FFh, 0E6h, 000h, 0E6h, 000h, 0E6h, 000h, 0E6h, 000h, 0E6h, 000h
    db 0E6h, 000h, 0E6h, 000h, 0E6h, 000h, 0E6h, 000h, 0E6h, 000h, 0E6h, 000h, 0E6h, 000h, 0E6h, 000h
    db 0E7h, 000h, 0FFh, 0FFh, 0E8h, 000h, 0FFh, 0FFh, 079h, 001h, 079h, 001h, 07Ah, 001h, 07Ah, 001h
    db 0FFh, 0FFh, 07Dh, 001h, 07Eh, 001h, 07Fh, 001h, 0FFh, 0FFh, 092h, 001h, 093h, 001h, 094h, 001h
    db 095h, 001h, 096h, 001h, 097h, 001h, 098h, 001h, 099h, 001h, 09Ah, 001h, 0FFh, 0FFh, 089h, 001h
    db 08Ah, 001h, 08Bh, 001h, 08Ch, 001h, 08Dh, 001h, 08Eh, 001h, 08Fh, 001h, 090h, 001h, 091h, 001h
    db 0FFh, 0FFh, 09Bh, 001h, 09Ch, 001h, 09Dh, 001h, 09Eh, 001h, 09Fh, 001h, 0A0h, 001h, 0A1h, 001h
    db 0A2h, 001h, 0A3h, 001h, 0FFh, 0FFh, 0A4h, 001h, 0A5h, 001h, 0A6h, 001h, 0A7h, 001h, 0A8h, 001h
    db 0A9h, 001h, 0AAh, 001h, 0ABh, 001h, 0ACh, 001h, 0FFh, 0FFh, 07Bh, 001h, 07Ch, 001h, 0FFh, 0FFh
    db 0C8h, 001h, 0C9h, 001h, 0CAh, 001h, 0CBh, 001h, 0CCh, 001h, 0CDh, 001h, 0CEh, 001h, 0CFh, 001h
    db 0D0h, 001h, 0FFh, 0FFh, 0BFh, 001h, 0C0h, 001h, 0C1h, 001h, 0C2h, 001h, 0C3h, 001h, 0C4h, 001h
    db 0C5h, 001h, 0C6h, 001h, 0C7h, 001h, 0FFh, 0FFh, 0F1h, 001h, 0F1h, 001h, 0F2h, 001h, 0F2h, 001h
    db 0FFh, 0FFh, 0F7h, 001h, 0F8h, 001h, 0F9h, 001h, 0FFh, 0FFh, 005h, 002h, 006h, 002h, 007h, 002h
    db 008h, 002h, 009h, 002h, 00Ah, 002h, 00Bh, 002h, 00Ch, 002h, 00Dh, 002h, 0FFh, 0FFh, 0FCh, 001h
    db 0FDh, 001h, 0FEh, 001h, 0FFh, 001h, 000h, 002h, 001h, 002h, 002h, 002h, 003h, 002h, 004h, 002h
    db 0FFh, 0FFh, 00Eh, 002h, 00Fh, 002h, 010h, 002h, 011h, 002h, 012h, 002h, 013h, 002h, 014h, 002h
    db 015h, 002h, 016h, 002h, 0FFh, 0FFh, 017h, 002h, 018h, 002h, 019h, 002h, 01Ah, 002h, 01Bh, 002h
    db 01Ch, 002h, 01Dh, 002h, 01Eh, 002h, 01Fh, 002h, 0FFh, 0FFh, 0F3h, 001h, 0F4h, 001h, 0F5h, 001h
    db 0F6h, 001h, 0FFh, 0FFh, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h
    db 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h
    db 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h, 02Bh, 001h
    db 02Bh, 001h, 02Bh, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h
    db 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ch, 001h, 02Ch, 001h
    db 02Ch, 001h, 02Ch, 001h, 02Ch, 001h, 02Ch, 001h, 02Ch, 001h, 02Ch, 001h, 02Ch, 001h, 02Ch, 001h
    db 02Ch, 001h, 02Ch, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h
    db 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 02Ah, 001h, 0FFh, 0FFh, 03Eh, 001h
    db 03Fh, 001h, 040h, 001h, 041h, 001h, 042h, 001h, 043h, 001h, 044h, 001h, 045h, 001h, 046h, 001h
    db 0FFh, 0FFh, 035h, 001h, 036h, 001h, 037h, 001h, 038h, 001h, 039h, 001h, 03Ah, 001h, 03Bh, 001h
    db 03Ch, 001h, 03Dh, 001h, 0FFh, 0FFh, 047h, 001h, 048h, 001h, 049h, 001h, 04Ah, 001h, 04Bh, 001h
    db 04Ch, 001h, 04Dh, 001h, 04Eh, 001h, 04Fh, 001h, 0FFh, 0FFh, 050h, 001h, 051h, 001h, 052h, 001h
    db 053h, 001h, 054h, 001h, 055h, 001h, 056h, 001h, 057h, 001h, 058h, 001h, 0FFh, 0FFh, 02Dh, 001h
    db 02Eh, 001h, 02Fh, 001h, 0FFh, 0FFh, 030h, 001h, 031h, 001h, 032h, 001h, 0FFh, 0FFh, 062h, 001h
    db 063h, 001h, 064h, 001h, 065h, 001h, 066h, 001h, 067h, 001h, 068h, 001h, 069h, 001h, 06Ah, 001h
    db 0FFh, 0FFh, 059h, 001h, 05Ah, 001h, 05Bh, 001h, 05Ch, 001h, 05Dh, 001h, 05Eh, 001h, 05Fh, 001h
    db 060h, 001h, 061h, 001h, 0FFh, 0FFh, 0FFh, 0FFh, 058h, 013h, 07Ch, 011h, 0DAh, 012h, 040h, 010h
    db 0E2h, 010h, 0F6h, 013h, 05Ch, 014h, 0A2h, 014h, 000h, 015h, 04Eh, 015h, 094h, 015h, 01Ah, 016h
    db 070h, 016h, 0CEh, 016h, 014h, 017h, 0FFh, 0FFh, 091h, 000h, 004h, 000h, 002h, 000h, 00Eh, 01Ch
    db 0F0h, 0FFh, 0DAh, 000h, 000h, 008h, 0DBh, 000h, 000h, 008h, 0DCh, 000h, 000h, 008h, 0DDh, 000h
    db 000h, 008h, 0DEh, 000h, 000h, 008h, 0DFh, 000h, 000h, 008h, 000h, 080h, 0DAh, 000h, 000h, 000h
    db 0DAh, 000h, 000h, 000h, 0DBh, 000h, 000h, 000h, 0DBh, 000h, 000h, 000h, 0DCh, 000h, 000h, 000h
    db 0DCh, 000h, 000h, 000h, 0DDh, 000h, 000h, 000h, 0DDh, 000h, 000h, 000h, 0DEh, 000h, 000h, 000h
    db 0DEh, 000h, 000h, 000h, 0DFh, 000h, 000h, 000h, 0DFh, 000h, 000h, 000h, 0FDh, 0FFh, 0DAh, 000h
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0DBh, 000h, 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0DCh, 000h
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0DDh, 000h, 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0DEh, 000h
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0DFh, 000h, 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0DAh, 000h
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0DBh, 000h, 000h, 000h, 000h, 080h, 0B0h, 0FFh, 0DCh, 000h
    db 000h, 000h, 000h, 080h, 0D9h, 000h, 000h, 000h, 000h, 080h, 099h, 000h, 06Ah, 000h, 002h, 000h
    db 00Eh, 01Ch, 02Eh, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F6h, 0FFh, 0ECh, 001h, 000h, 000h
    db 000h, 080h, 0EDh, 001h, 000h, 008h, 0F8h, 0FFh, 0EDh, 001h, 000h, 000h, 000h, 080h, 0EEh, 001h
    db 000h, 008h, 0FBh, 0FFh, 0EEh, 001h, 000h, 000h, 000h, 080h, 0EFh, 001h, 000h, 008h, 0FBh, 0FFh
    db 0EFh, 001h, 000h, 000h, 000h, 080h, 0F0h, 001h, 000h, 008h, 0F6h, 0FFh, 0F0h, 001h, 000h, 000h
    db 000h, 080h, 0FDh, 0FFh, 092h, 001h, 000h, 000h, 092h, 001h, 0F8h, 000h, 093h, 001h, 000h, 000h
    db 093h, 001h, 0F8h, 000h, 094h, 001h, 000h, 000h, 094h, 001h, 0F8h, 000h, 095h, 001h, 000h, 000h
    db 095h, 001h, 0F8h, 000h, 096h, 001h, 000h, 000h, 096h, 001h, 0F8h, 000h, 097h, 001h, 000h, 000h
    db 097h, 001h, 0F8h, 000h, 098h, 001h, 000h, 000h, 098h, 001h, 0F8h, 000h, 099h, 001h, 000h, 000h
    db 099h, 001h, 0F8h, 000h, 09Ah, 001h, 000h, 000h, 09Ah, 001h, 0F8h, 000h, 000h, 080h, 0FFh, 07Fh
    db 000h, 000h, 000h, 080h, 07Ch, 000h, 06Eh, 000h, 002h, 000h, 00Eh, 01Ch, 0CFh, 0FEh, 0FFh, 07Fh
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 089h, 001h, 000h, 000h, 089h, 001h, 008h, 000h, 08Ah, 001h
    db 000h, 000h, 08Ah, 001h, 008h, 000h, 08Bh, 001h, 000h, 000h, 08Bh, 001h, 008h, 000h, 08Ch, 001h
    db 000h, 000h, 08Ch, 001h, 008h, 000h, 08Dh, 001h, 000h, 000h, 08Dh, 001h, 008h, 000h, 08Eh, 001h
    db 000h, 000h, 08Eh, 001h, 008h, 000h, 08Fh, 001h, 000h, 000h, 08Fh, 001h, 008h, 000h, 090h, 001h
    db 000h, 000h, 090h, 001h, 008h, 000h, 091h, 001h, 000h, 000h, 091h, 001h, 008h, 000h, 000h, 080h
    db 0DDh, 0FFh, 079h, 001h, 000h, 000h, 000h, 080h, 0FBh, 0FFh, 0B6h, 001h, 0F8h, 000h, 0B6h, 001h
    db 000h, 000h, 0B7h, 001h, 0F8h, 000h, 0B7h, 001h, 000h, 000h, 0B8h, 001h, 0F8h, 000h, 0B8h, 001h
    db 000h, 000h, 0B9h, 001h, 0F8h, 000h, 0B9h, 001h, 000h, 000h, 0BAh, 001h, 0F8h, 000h, 0BAh, 001h
    db 000h, 000h, 0BBh, 001h, 0F8h, 000h, 0BBh, 001h, 000h, 000h, 0BCh, 001h, 0F8h, 000h, 0BCh, 001h
    db 000h, 000h, 0BDh, 001h, 0F8h, 000h, 0BDh, 001h, 000h, 000h, 0BEh, 001h, 0F8h, 000h, 0BEh, 001h
    db 000h, 000h, 000h, 080h, 0D9h, 001h, 000h, 000h, 0D9h, 001h, 000h, 000h, 0DAh, 001h, 000h, 000h
    db 0DAh, 001h, 000h, 000h, 0DBh, 001h, 000h, 000h, 0DBh, 001h, 000h, 000h, 0DCh, 001h, 000h, 000h
    db 0DCh, 001h, 000h, 000h, 0DDh, 001h, 000h, 000h, 0DDh, 001h, 000h, 000h, 0CEh, 0FFh, 0DEh, 001h
    db 000h, 000h, 000h, 080h, 0F6h, 0FFh, 083h, 001h, 000h, 000h, 000h, 080h, 0B0h, 0FFh, 084h, 001h
    db 000h, 000h, 000h, 080h, 0F9h, 0FFh, 079h, 001h, 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h
    db 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h
    db 000h, 000h, 079h, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h
    db 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h
    db 000h, 000h, 07Ah, 001h, 000h, 000h, 000h, 080h, 0F8h, 0FFh, 0E7h, 001h, 000h, 000h, 000h, 080h
    db 0F8h, 0FFh, 0E8h, 001h, 000h, 000h, 000h, 080h, 0F8h, 0FFh, 0E9h, 001h, 000h, 000h, 000h, 080h
    db 0F8h, 0FFh, 0EAh, 001h, 000h, 000h, 000h, 080h, 0F8h, 0FFh, 0EBh, 001h, 000h, 000h, 000h, 080h
    db 000h, 080h, 022h, 000h, 06Ah, 000h, 002h, 000h, 00Eh, 01Ch, 0A8h, 0FDh, 02Ah, 001h, 000h, 000h
    db 000h, 080h, 0F9h, 0FFh, 035h, 001h, 008h, 000h, 035h, 001h, 000h, 000h, 036h, 001h, 008h, 000h
    db 036h, 001h, 000h, 000h, 037h, 001h, 008h, 000h, 037h, 001h, 000h, 000h, 038h, 001h, 008h, 000h
    db 038h, 001h, 000h, 000h, 039h, 001h, 008h, 000h, 039h, 001h, 000h, 000h, 03Ah, 001h, 008h, 000h
    db 03Ah, 001h, 000h, 000h, 03Bh, 001h, 008h, 000h, 03Bh, 001h, 000h, 000h, 03Ch, 001h, 008h, 000h
    db 03Ch, 001h, 000h, 000h, 03Dh, 001h, 008h, 000h, 03Dh, 001h, 000h, 000h, 000h, 080h, 0F6h, 0FFh
    db 075h, 001h, 000h, 000h, 000h, 080h, 0FAh, 0FFh, 076h, 001h, 000h, 000h, 000h, 080h, 0FAh, 0FFh
    db 077h, 001h, 000h, 000h, 000h, 080h, 0FAh, 0FFh, 078h, 001h, 000h, 000h, 000h, 080h, 000h, 080h
    db 091h, 000h, 051h, 000h, 002h, 000h, 00Eh, 01Ch, 078h, 0FEh, 0FFh, 07Fh, 000h, 000h, 000h, 080h
    db 0D2h, 0FFh, 0E9h, 000h, 0F8h, 000h, 0E9h, 000h, 000h, 000h, 000h, 080h, 0FEh, 0FFh, 0E9h, 000h
    db 000h, 000h, 000h, 080h, 0E9h, 000h, 0F8h, 0F3h, 0E9h, 000h, 0F8h, 0F4h, 0E9h, 000h, 0F8h, 0F5h
    db 0E9h, 000h, 0F8h, 0F6h, 0E9h, 000h, 0F8h, 0F7h, 0E9h, 000h, 0F8h, 0F8h, 0E9h, 000h, 0F8h, 0F9h
    db 0E9h, 000h, 0F8h, 0FAh, 0E9h, 000h, 0F8h, 0FBh, 0E9h, 000h, 0F8h, 0FCh, 0E9h, 000h, 0F8h, 0FDh
    db 0E9h, 000h, 0F8h, 0FEh, 0E9h, 000h, 0F8h, 0FFh, 0FDh, 0FFh, 0E9h, 000h, 0F8h, 000h, 000h, 080h
    db 0E9h, 000h, 0F8h, 001h, 0E9h, 000h, 0F8h, 002h, 0E9h, 000h, 0F8h, 003h, 0E9h, 000h, 0F8h, 004h
    db 0E9h, 000h, 0F8h, 005h, 0E9h, 000h, 0F8h, 006h, 0E9h, 000h, 0F8h, 007h, 0E9h, 000h, 0F8h, 008h
    db 0E9h, 000h, 0F8h, 009h, 0E9h, 000h, 0F8h, 00Ah, 0E9h, 000h, 0F8h, 00Bh, 0E9h, 000h, 0F8h, 00Ch
    db 0E9h, 000h, 0F8h, 00Dh, 0FBh, 0FFh, 0E9h, 000h, 0F8h, 00Fh, 000h, 080h, 000h, 080h, 06Bh, 000h
    db 053h, 000h, 002h, 000h, 00Eh, 01Ch, 09Fh, 0FCh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F6h, 0FFh
    db 026h, 001h, 0F8h, 0F8h, 000h, 080h, 0F6h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F6h, 0FFh
    db 028h, 001h, 008h, 0F8h, 000h, 080h, 0F6h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F6h, 0FFh
    db 026h, 001h, 0F8h, 0F8h, 000h, 080h, 0F6h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F6h, 0FFh
    db 028h, 001h, 008h, 0F8h, 000h, 080h, 0F6h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F6h, 0FFh
    db 026h, 001h, 0F8h, 0F8h, 000h, 080h, 0F6h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0FFh, 07Fh
    db 000h, 000h, 000h, 080h, 06Bh, 000h, 053h, 000h, 002h, 000h, 00Eh, 01Ch, 08Ah, 0FCh, 0FFh, 07Fh
    db 000h, 000h, 000h, 080h, 0F0h, 0FFh, 026h, 001h, 0F0h, 0F8h, 000h, 080h, 0F0h, 0FFh, 027h, 001h
    db 0F0h, 0F8h, 000h, 080h, 0F0h, 0FFh, 028h, 001h, 010h, 0F8h, 000h, 080h, 0F0h, 0FFh, 027h, 001h
    db 010h, 0F8h, 000h, 080h, 0F0h, 0FFh, 026h, 001h, 0F0h, 0F8h, 000h, 080h, 0F0h, 0FFh, 027h, 001h
    db 0F0h, 0F8h, 000h, 080h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 06Bh, 000h, 053h, 000h, 002h, 000h
    db 00Eh, 01Ch, 075h, 0FCh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F5h, 0FFh, 026h, 001h, 0F8h, 0F8h
    db 000h, 080h, 0F5h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F4h, 0FFh, 028h, 001h, 008h, 0F8h
    db 000h, 080h, 0F4h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F5h, 0FFh, 026h, 001h, 0F8h, 0F8h
    db 000h, 080h, 0F5h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F4h, 0FFh, 028h, 001h, 008h, 0F8h
    db 000h, 080h, 0F4h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F5h, 0FFh, 026h, 001h, 0F8h, 0F8h
    db 000h, 080h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 06Bh, 000h, 053h, 000h, 002h, 000h, 00Eh, 01Ch
    db 060h, 0FCh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F1h, 0FFh, 026h, 001h, 0E8h, 0F8h, 000h, 080h
    db 0F1h, 0FFh, 027h, 001h, 0E8h, 0F8h, 000h, 080h, 0F2h, 0FFh, 028h, 001h, 018h, 0F8h, 000h, 080h
    db 0F2h, 0FFh, 027h, 001h, 018h, 0F8h, 000h, 080h, 0F1h, 0FFh, 026h, 001h, 0E8h, 0F8h, 000h, 080h
    db 0F1h, 0FFh, 027h, 001h, 0E8h, 0F8h, 000h, 080h, 0F2h, 0FFh, 028h, 001h, 018h, 0F8h, 000h, 080h
    db 0FFh, 07Fh, 000h, 000h, 000h, 080h, 06Bh, 000h, 053h, 000h, 002h, 000h, 00Eh, 01Ch, 04Bh, 0FCh
    db 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0EDh, 0FFh, 026h, 001h, 0F0h, 0F8h, 000h, 080h, 0F0h, 0FFh
    db 027h, 001h, 0F0h, 0F8h, 000h, 080h, 0F2h, 0FFh, 028h, 001h, 010h, 0F8h, 000h, 080h, 0F2h, 0FFh
    db 027h, 001h, 010h, 0F8h, 000h, 080h, 0EDh, 0FFh, 026h, 001h, 0F0h, 0F8h, 000h, 080h, 0F2h, 0FFh
    db 027h, 001h, 0F0h, 0F8h, 000h, 080h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 06Bh, 000h, 053h, 000h
    db 002h, 000h, 00Eh, 01Ch, 036h, 0FCh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F9h, 0FFh, 026h, 001h
    db 0F8h, 0F8h, 000h, 080h, 0F9h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F9h, 0FFh, 028h, 001h
    db 008h, 0F8h, 000h, 080h, 0F9h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F9h, 0FFh, 026h, 001h
    db 0F8h, 0F8h, 000h, 080h, 0F8h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F9h, 0FFh, 028h, 001h
    db 008h, 0F8h, 000h, 080h, 0FAh, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F9h, 0FFh, 026h, 001h
    db 0F8h, 0F8h, 000h, 080h, 0F8h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F9h, 0FFh, 026h, 001h
    db 008h, 0F8h, 000h, 080h, 0F8h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F9h, 0FFh, 026h, 001h
    db 0F8h, 0F8h, 000h, 080h, 0FAh, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0FFh, 07Fh, 000h, 000h
    db 000h, 080h, 06Bh, 000h, 053h, 000h, 002h, 000h, 00Eh, 01Ch, 021h, 0FCh, 0FFh, 07Fh, 000h, 000h
    db 000h, 080h, 0F2h, 0FFh, 026h, 001h, 0F8h, 0F8h, 000h, 080h, 0F5h, 0FFh, 027h, 001h, 0F8h, 0F8h
    db 000h, 080h, 0F5h, 0FFh, 028h, 001h, 008h, 0F8h, 000h, 080h, 0F3h, 0FFh, 027h, 001h, 008h, 0F8h
    db 000h, 080h, 0F1h, 0FFh, 026h, 001h, 0F8h, 0F8h, 000h, 080h, 0F3h, 0FFh, 027h, 001h, 0F8h, 0F8h
    db 000h, 080h, 0F4h, 0FFh, 028h, 001h, 008h, 0F8h, 000h, 080h, 0F4h, 0FFh, 027h, 001h, 008h, 0F8h
    db 000h, 080h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 06Bh, 000h, 053h, 000h, 002h, 000h, 00Eh, 01Ch
    db 00Ch, 0FCh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F6h, 0FFh, 026h, 001h, 0E8h, 0F8h, 000h, 080h
    db 0F5h, 0FFh, 027h, 001h, 0E8h, 0F8h, 000h, 080h, 0F5h, 0FFh, 028h, 001h, 018h, 0F8h, 000h, 080h
    db 0F6h, 0FFh, 027h, 001h, 018h, 0F8h, 000h, 080h, 0F6h, 0FFh, 026h, 001h, 0E8h, 0F8h, 000h, 080h
    db 0F5h, 0FFh, 027h, 001h, 0E8h, 0F8h, 000h, 080h, 0F5h, 0FFh, 028h, 001h, 018h, 0F8h, 000h, 080h
    db 0F5h, 0FFh, 027h, 001h, 018h, 0F8h, 000h, 080h, 0F6h, 0FFh, 026h, 001h, 0E8h, 0F8h, 000h, 080h
    db 0FFh, 07Fh, 000h, 000h, 000h, 080h, 06Bh, 000h, 053h, 000h, 002h, 000h, 00Eh, 01Ch, 0F7h, 0FBh
    db 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0EEh, 0FFh, 026h, 001h, 0F0h, 0F8h, 000h, 080h, 0EFh, 0FFh
    db 027h, 001h, 0F0h, 0F8h, 000h, 080h, 0F3h, 0FFh, 028h, 001h, 010h, 0F8h, 000h, 080h, 0F2h, 0FFh
    db 027h, 001h, 010h, 0F8h, 000h, 080h, 0EEh, 0FFh, 026h, 001h, 0F0h, 0F8h, 000h, 080h, 0F1h, 0FFh
    db 027h, 001h, 0F0h, 0F8h, 000h, 080h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 06Bh, 000h, 053h, 000h
    db 002h, 000h, 00Eh, 01Ch, 0E2h, 0FBh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F8h, 0FFh, 026h, 001h
    db 0F8h, 0F8h, 000h, 080h, 0F9h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F9h, 0FFh, 028h, 001h
    db 008h, 0F8h, 000h, 080h, 0F8h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F7h, 0FFh, 026h, 001h
    db 0F8h, 0F8h, 000h, 080h, 0F8h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F9h, 0FFh, 028h, 001h
    db 008h, 0F8h, 000h, 080h, 0F9h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F8h, 0FFh, 026h, 001h
    db 0F8h, 0F8h, 000h, 080h, 0F8h, 0FFh, 027h, 001h, 0F8h, 0F8h, 000h, 080h, 0F7h, 0FFh, 026h, 001h
    db 008h, 0F8h, 000h, 080h, 0F9h, 0FFh, 027h, 001h, 008h, 0F8h, 000h, 080h, 0F8h, 0FFh, 026h, 001h
    db 0F8h, 0F8h, 000h, 080h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0C2h, 01Ah, 0A0h, 017h, 0BCh, 01Ch
    db 0FEh, 01Bh, 080h, 01Bh, 002h, 01Eh, 0FFh, 0FFh, 007h, 001h, 06Eh, 000h, 002h, 000h, 00Eh, 01Ch
    db 0F6h, 0FFh, 0D1h, 001h, 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h
    db 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h
    db 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h
    db 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h, 000h, 000h, 0D1h, 001h
    db 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h
    db 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h
    db 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h
    db 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h
    db 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h
    db 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h
    db 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h
    db 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h, 000h, 000h, 0D3h, 001h
    db 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h
    db 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h
    db 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h
    db 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h, 000h, 000h, 0D2h, 001h
    db 000h, 000h, 000h, 080h, 0B0h, 0FFh, 0D8h, 001h, 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0D4h, 001h
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0D5h, 001h, 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0D6h, 001h
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 0D7h, 001h, 000h, 000h, 000h, 080h, 0FDh, 0FFh, 080h, 001h
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 081h, 001h, 000h, 000h, 000h, 080h, 04Ch, 0FFh, 082h, 001h
    db 000h, 000h, 000h, 080h, 0FDh, 0FFh, 089h, 001h, 008h, 000h, 089h, 001h, 008h, 000h, 08Ah, 001h
    db 008h, 000h, 08Ah, 001h, 008h, 000h, 08Bh, 001h, 008h, 000h, 08Bh, 001h, 008h, 000h, 08Ch, 001h
    db 008h, 000h, 08Ch, 001h, 008h, 000h, 08Dh, 001h, 008h, 000h, 08Dh, 001h, 008h, 000h, 08Eh, 001h
    db 008h, 000h, 08Eh, 001h, 008h, 000h, 08Fh, 001h, 008h, 000h, 08Fh, 001h, 008h, 000h, 090h, 001h
    db 008h, 000h, 090h, 001h, 008h, 000h, 091h, 001h, 008h, 000h, 091h, 001h, 008h, 000h, 000h, 080h
    db 0C4h, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F1h, 0FFh, 0B6h, 001h, 0F8h, 000h, 0B6h, 001h
    db 000h, 000h, 0B7h, 001h, 0F8h, 000h, 0B7h, 001h, 000h, 000h, 0B8h, 001h, 0F8h, 000h, 0B8h, 001h
    db 000h, 000h, 0B9h, 001h, 0F8h, 000h, 0B9h, 001h, 000h, 000h, 0BAh, 001h, 0F8h, 000h, 0BAh, 001h
    db 000h, 000h, 0BBh, 001h, 0F8h, 000h, 0BBh, 001h, 000h, 000h, 0BCh, 001h, 0F8h, 000h, 0BCh, 001h
    db 000h, 000h, 0BDh, 001h, 0F8h, 000h, 0BDh, 001h, 000h, 000h, 0BEh, 001h, 0F8h, 000h, 0BEh, 001h
    db 000h, 000h, 000h, 080h, 0D9h, 001h, 000h, 000h, 0D9h, 001h, 000h, 000h, 0DAh, 001h, 000h, 000h
    db 0DAh, 001h, 000h, 000h, 0DBh, 001h, 000h, 000h, 0DBh, 001h, 000h, 000h, 0DCh, 001h, 000h, 000h
    db 0DCh, 001h, 000h, 000h, 0DDh, 001h, 000h, 000h, 0DDh, 001h, 000h, 000h, 0CEh, 0FFh, 0DEh, 001h
    db 000h, 000h, 000h, 080h, 0F7h, 0FFh, 079h, 001h, 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h
    db 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h
    db 000h, 000h, 079h, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h
    db 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h
    db 000h, 000h, 07Ah, 001h, 000h, 000h, 000h, 080h, 0F6h, 0FFh, 083h, 001h, 000h, 000h, 000h, 080h
    db 0D4h, 0FEh, 084h, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 0E1h, 001h, 000h, 000h, 000h, 080h
    db 0FCh, 0FFh, 0E2h, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 0E3h, 001h, 000h, 000h, 000h, 080h
    db 0FCh, 0FFh, 0E4h, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 0E5h, 001h, 000h, 000h, 000h, 080h
    db 09Ch, 0FFh, 0E6h, 001h, 000h, 000h, 000h, 080h, 0F0h, 0FFh, 085h, 001h, 000h, 000h, 085h, 001h
    db 000h, 000h, 085h, 001h, 000h, 000h, 085h, 001h, 000h, 000h, 085h, 001h, 000h, 000h, 085h, 001h
    db 000h, 000h, 086h, 001h, 000h, 000h, 086h, 001h, 000h, 000h, 086h, 001h, 000h, 000h, 086h, 001h
    db 000h, 000h, 086h, 001h, 000h, 000h, 086h, 001h, 000h, 000h, 000h, 080h, 0FDh, 0FFh, 092h, 001h
    db 0F8h, 000h, 092h, 001h, 000h, 000h, 093h, 001h, 0F8h, 000h, 093h, 001h, 000h, 000h, 094h, 001h
    db 0F8h, 000h, 094h, 001h, 000h, 000h, 095h, 001h, 0F8h, 000h, 095h, 001h, 000h, 000h, 096h, 001h
    db 0F8h, 000h, 096h, 001h, 000h, 000h, 097h, 001h, 0F8h, 000h, 097h, 001h, 000h, 000h, 098h, 001h
    db 0F8h, 000h, 098h, 001h, 000h, 000h, 099h, 001h, 0F8h, 000h, 099h, 001h, 000h, 000h, 09Ah, 001h
    db 0F8h, 000h, 09Ah, 001h, 000h, 000h, 000h, 080h, 000h, 080h, 009h, 001h, 048h, 000h, 002h, 000h
    db 00Eh, 01Ch, 099h, 0FDh, 01Dh, 001h, 000h, 000h, 000h, 080h, 01Dh, 001h, 000h, 001h, 01Dh, 001h
    db 000h, 002h, 01Dh, 001h, 000h, 003h, 01Dh, 001h, 000h, 004h, 01Dh, 001h, 000h, 005h, 01Dh, 001h
    db 000h, 006h, 01Dh, 001h, 000h, 007h, 01Dh, 001h, 000h, 008h, 01Dh, 001h, 000h, 009h, 01Dh, 001h
    db 000h, 00Ah, 01Dh, 001h, 000h, 00Bh, 01Dh, 001h, 000h, 00Ch, 01Dh, 001h, 000h, 00Dh, 0F9h, 0FFh
    db 01Dh, 001h, 000h, 00Fh, 000h, 080h, 01Dh, 001h, 008h, 0F3h, 01Dh, 001h, 008h, 0F4h, 01Dh, 001h
    db 008h, 0F5h, 01Dh, 001h, 008h, 0F6h, 01Dh, 001h, 008h, 0F7h, 01Dh, 001h, 008h, 0F8h, 01Dh, 001h
    db 008h, 0F9h, 01Dh, 001h, 008h, 0FAh, 01Dh, 001h, 008h, 0FBh, 01Dh, 001h, 008h, 0FCh, 01Dh, 001h
    db 008h, 0FDh, 01Dh, 001h, 008h, 0FEh, 01Dh, 001h, 008h, 0FFh, 01Dh, 001h, 008h, 001h, 01Dh, 001h
    db 008h, 002h, 01Dh, 001h, 008h, 003h, 01Dh, 001h, 008h, 004h, 01Dh, 001h, 008h, 005h, 01Dh, 001h
    db 008h, 006h, 01Dh, 001h, 008h, 007h, 01Dh, 001h, 008h, 008h, 01Dh, 001h, 008h, 009h, 01Dh, 001h
    db 008h, 00Ah, 01Dh, 001h, 008h, 00Bh, 01Dh, 001h, 008h, 00Ch, 01Dh, 001h, 008h, 00Dh, 0FCh, 0FFh
    db 01Dh, 001h, 008h, 00Fh, 000h, 080h, 000h, 080h, 0E8h, 000h, 057h, 000h, 002h, 000h, 00Eh, 01Ch
    db 060h, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0BAh, 0FFh, 003h, 001h, 000h, 000h, 000h, 080h
    db 09Ch, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0BAh, 0FFh, 003h, 001h, 000h, 000h, 000h, 080h
    db 006h, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0BCh, 0FFh, 006h, 001h, 000h, 000h, 000h, 080h
    db 0E4h, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F6h, 0FFh, 004h, 001h, 000h, 000h, 000h, 080h
    db 0D8h, 0FFh, 005h, 001h, 000h, 000h, 000h, 080h, 0D8h, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h
    db 0CEh, 0FFh, 002h, 001h, 000h, 000h, 000h, 080h, 07Ch, 0FCh, 0FFh, 07Fh, 000h, 000h, 000h, 080h
    db 0A9h, 0FFh, 0FFh, 07Fh, 0F8h, 000h, 000h, 080h, 0BAh, 0FFh, 00Bh, 001h, 000h, 000h, 000h, 080h
    db 0FFh, 07Fh, 000h, 000h, 000h, 080h, 040h, 001h, 05Bh, 000h, 002h, 000h, 00Eh, 01Ch, 00Ch, 0FCh
    db 0D9h, 000h, 000h, 000h, 000h, 080h, 070h, 0FFh, 0D9h, 000h, 0F8h, 000h, 0D9h, 000h, 000h, 000h
    db 000h, 080h, 0FDh, 0FFh, 0D9h, 000h, 000h, 000h, 000h, 080h, 0D9h, 000h, 000h, 008h, 0D9h, 000h
    db 000h, 000h, 0D9h, 000h, 000h, 008h, 0D9h, 000h, 000h, 000h, 0D9h, 000h, 000h, 0F8h, 0D9h, 000h
    db 000h, 000h, 0D9h, 000h, 000h, 0F8h, 0D9h, 000h, 000h, 000h, 0D9h, 000h, 0F8h, 0F3h, 0D9h, 000h
    db 0F8h, 0F4h, 0D9h, 000h, 0F8h, 0F5h, 0D9h, 000h, 0F8h, 0F6h, 0D9h, 000h, 0F8h, 0F7h, 0D9h, 000h
    db 0F8h, 0F8h, 0D9h, 000h, 0F8h, 0F9h, 0D9h, 000h, 0F8h, 0FAh, 0D9h, 000h, 0F8h, 0FBh, 0D9h, 000h
    db 0F8h, 0FCh, 0D9h, 000h, 0F8h, 0FDh, 0D9h, 000h, 0F8h, 0FEh, 0D9h, 000h, 0F8h, 0FFh, 0FDh, 0FFh
    db 0D9h, 000h, 0F8h, 000h, 000h, 080h, 0D9h, 000h, 0F8h, 001h, 0D9h, 000h, 0F8h, 002h, 0D9h, 000h
    db 0F8h, 003h, 0D9h, 000h, 0F8h, 004h, 0D9h, 000h, 0F8h, 005h, 0D9h, 000h, 0F8h, 006h, 0D9h, 000h
    db 0F8h, 007h, 0D9h, 000h, 0F8h, 008h, 0D9h, 000h, 0F8h, 009h, 0D9h, 000h, 0F8h, 00Ah, 0D9h, 000h
    db 0F8h, 00Bh, 0D9h, 000h, 0F8h, 00Ch, 0D9h, 000h, 0F8h, 00Dh, 0FBh, 0FFh, 0D9h, 000h, 0F8h, 00Fh
    db 000h, 080h, 000h, 080h, 040h, 001h, 06Ah, 000h, 002h, 000h, 089h, 009h, 088h, 0FAh, 0D9h, 000h
    db 000h, 000h, 000h, 080h, 0FAh, 0FFh, 03Eh, 001h, 0F8h, 000h, 03Eh, 001h, 0F8h, 000h, 03Fh, 001h
    db 0F8h, 000h, 03Fh, 001h, 0F8h, 000h, 040h, 001h, 0F8h, 000h, 040h, 001h, 0F8h, 000h, 041h, 001h
    db 0F8h, 000h, 041h, 001h, 0F8h, 000h, 042h, 001h, 0F8h, 000h, 042h, 001h, 0F8h, 000h, 043h, 001h
    db 0F8h, 000h, 043h, 001h, 0F8h, 000h, 044h, 001h, 0F8h, 000h, 044h, 001h, 0F8h, 000h, 045h, 001h
    db 0F8h, 000h, 045h, 001h, 0F8h, 000h, 046h, 001h, 0F8h, 000h, 046h, 001h, 0F8h, 000h, 000h, 080h
    db 0D8h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0C4h, 0FFh, 02Bh, 001h, 000h, 000h, 000h, 080h
    db 0CEh, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D8h, 0FFh, 02Ch, 001h, 000h, 000h, 000h, 080h
    db 0C4h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0C4h, 0FFh, 02Bh, 001h, 000h, 000h, 000h, 080h
    db 0D8h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D8h, 0FFh, 02Ch, 001h, 000h, 000h, 000h, 080h
    db 0FCh, 0FFh, 070h, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 071h, 001h, 000h, 000h, 000h, 080h
    db 0FCh, 0FFh, 072h, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 073h, 001h, 000h, 000h, 000h, 080h
    db 0FCh, 0FFh, 074h, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 06Bh, 001h, 000h, 000h, 000h, 080h
    db 0FCh, 0FFh, 06Ch, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 06Dh, 001h, 000h, 000h, 000h, 080h
    db 0FCh, 0FFh, 06Eh, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 06Fh, 001h, 000h, 000h, 000h, 080h
    db 0FAh, 0FFh, 035h, 001h, 008h, 000h, 035h, 001h, 008h, 000h, 036h, 001h, 008h, 000h, 036h, 001h
    db 008h, 000h, 037h, 001h, 008h, 000h, 037h, 001h, 008h, 000h, 038h, 001h, 008h, 000h, 038h, 001h
    db 008h, 000h, 039h, 001h, 008h, 000h, 039h, 001h, 008h, 000h, 03Ah, 001h, 008h, 000h, 03Ah, 001h
    db 008h, 000h, 03Bh, 001h, 008h, 000h, 03Bh, 001h, 008h, 000h, 03Ch, 001h, 008h, 000h, 03Ch, 001h
    db 008h, 000h, 03Dh, 001h, 008h, 000h, 03Dh, 001h, 008h, 000h, 000h, 080h, 0A1h, 0FFh, 02Ah, 001h
    db 000h, 000h, 000h, 080h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0B4h, 000h, 053h, 000h, 002h, 000h
    db 00Eh, 01Ch, 0F2h, 0F9h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0BAh, 0FFh, 008h, 001h, 000h, 000h
    db 000h, 080h, 0E2h, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0BAh, 0FFh, 009h, 001h, 000h, 000h
    db 000h, 080h, 0E2h, 0FFh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0BFh, 0FFh, 00Ah, 001h, 000h, 000h
    db 000h, 080h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 04Ch, 01Eh, 0BEh, 01Fh, 040h, 021h, 008h, 024h
    db 0C2h, 022h, 0FFh, 0FFh, 04Bh, 001h, 086h, 000h, 002h, 000h, 00Eh, 01Ch, 0F6h, 0FFh, 092h, 001h
    db 0F8h, 000h, 092h, 001h, 0F8h, 000h, 093h, 001h, 0F8h, 000h, 093h, 001h, 0F8h, 000h, 094h, 001h
    db 0F8h, 000h, 094h, 001h, 0F8h, 000h, 095h, 001h, 0F8h, 000h, 095h, 001h, 0F8h, 000h, 096h, 001h
    db 0F8h, 000h, 096h, 001h, 0F8h, 000h, 097h, 001h, 0F8h, 000h, 097h, 001h, 0F8h, 000h, 098h, 001h
    db 0F8h, 000h, 098h, 001h, 0F8h, 000h, 099h, 001h, 0F8h, 000h, 099h, 001h, 0F8h, 000h, 09Ah, 001h
    db 0F8h, 000h, 09Ah, 001h, 0F8h, 000h, 000h, 080h, 0F9h, 0FFh, 07Dh, 001h, 000h, 000h, 07Dh, 001h
    db 000h, 000h, 07Dh, 001h, 000h, 000h, 07Dh, 001h, 000h, 000h, 07Dh, 001h, 000h, 000h, 07Dh, 001h
    db 000h, 000h, 07Eh, 001h, 000h, 000h, 07Eh, 001h, 000h, 000h, 07Eh, 001h, 000h, 000h, 07Eh, 001h
    db 000h, 000h, 07Eh, 001h, 000h, 000h, 07Eh, 001h, 000h, 000h, 07Fh, 001h, 000h, 000h, 07Fh, 001h
    db 000h, 000h, 07Fh, 001h, 000h, 000h, 07Fh, 001h, 000h, 000h, 07Fh, 001h, 000h, 000h, 07Fh, 001h
    db 000h, 000h, 000h, 080h, 0CEh, 0FFh, 083h, 001h, 000h, 000h, 000h, 080h, 0F9h, 0FFh, 092h, 001h
    db 0F8h, 000h, 092h, 001h, 0F8h, 000h, 093h, 001h, 0F8h, 000h, 093h, 001h, 0F8h, 000h, 094h, 001h
    db 0F8h, 000h, 094h, 001h, 0F8h, 000h, 095h, 001h, 0F8h, 000h, 095h, 001h, 0F8h, 000h, 096h, 001h
    db 0F8h, 000h, 096h, 001h, 0F8h, 000h, 097h, 001h, 0F8h, 000h, 097h, 001h, 0F8h, 000h, 098h, 001h
    db 0F8h, 000h, 098h, 001h, 0F8h, 000h, 099h, 001h, 0F8h, 000h, 099h, 001h, 0F8h, 000h, 09Ah, 001h
    db 0F8h, 000h, 09Ah, 001h, 0F8h, 000h, 000h, 080h, 0B2h, 0FFh, 079h, 001h, 000h, 000h, 079h, 001h
    db 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h, 000h, 000h, 079h, 001h
    db 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h
    db 000h, 000h, 07Ah, 001h, 000h, 000h, 07Ah, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 087h, 001h
    db 000h, 000h, 000h, 080h, 0FBh, 0FFh, 088h, 001h, 000h, 000h, 000h, 080h, 0FCh, 0FFh, 087h, 001h
    db 000h, 000h, 000h, 080h, 0F8h, 0FFh, 088h, 001h, 000h, 000h, 000h, 080h, 0FDh, 0FFh, 092h, 001h
    db 0F0h, 000h, 093h, 001h, 0F0h, 000h, 094h, 001h, 0F0h, 000h, 095h, 001h, 0F0h, 000h, 096h, 001h
    db 0F0h, 000h, 097h, 001h, 0F0h, 000h, 098h, 001h, 0F0h, 000h, 099h, 001h, 0F0h, 000h, 09Ah, 001h
    db 0F0h, 000h, 000h, 080h, 000h, 080h, 04Bh, 001h, 082h, 000h, 002h, 000h, 00Eh, 01Ch, 08Eh, 0FEh
    db 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F6h, 0FFh, 03Eh, 001h, 0F8h, 000h, 03Eh, 001h, 0F8h, 000h
    db 03Fh, 001h, 0F8h, 000h, 03Fh, 001h, 0F8h, 000h, 040h, 001h, 0F8h, 000h, 040h, 001h, 0F8h, 000h
    db 041h, 001h, 0F8h, 000h, 041h, 001h, 0F8h, 000h, 042h, 001h, 0F8h, 000h, 042h, 001h, 0F8h, 000h
    db 043h, 001h, 0F8h, 000h, 043h, 001h, 0F8h, 000h, 044h, 001h, 0F8h, 000h, 044h, 001h, 0F8h, 000h
    db 045h, 001h, 0F8h, 000h, 045h, 001h, 0F8h, 000h, 046h, 001h, 0F8h, 000h, 046h, 001h, 0F8h, 000h
    db 000h, 080h, 0D8h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0C4h, 0FFh, 02Bh, 001h, 000h, 000h
    db 000h, 080h, 0D8h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0FAh, 0FFh, 03Eh, 001h, 0F8h, 000h
    db 03Eh, 001h, 0F8h, 000h, 03Fh, 001h, 0F8h, 000h, 03Fh, 001h, 0F8h, 000h, 040h, 001h, 0F8h, 000h
    db 040h, 001h, 0F8h, 000h, 041h, 001h, 0F8h, 000h, 041h, 001h, 0F8h, 000h, 042h, 001h, 0F8h, 000h
    db 042h, 001h, 0F8h, 000h, 043h, 001h, 0F8h, 000h, 043h, 001h, 0F8h, 000h, 044h, 001h, 0F8h, 000h
    db 044h, 001h, 0F8h, 000h, 045h, 001h, 0F8h, 000h, 045h, 001h, 0F8h, 000h, 046h, 001h, 0F8h, 000h
    db 046h, 001h, 0F8h, 000h, 000h, 080h, 0D7h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh
    db 02Bh, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh
    db 02Ch, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh
    db 02Bh, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh
    db 02Ch, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh
    db 02Bh, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh
    db 02Ch, 001h, 000h, 000h, 000h, 080h, 0D7h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0D6h, 0FFh
    db 02Bh, 001h, 000h, 000h, 000h, 080h, 0D6h, 0FFh, 02Ah, 001h, 000h, 000h, 000h, 080h, 0FBh, 0FFh
    db 033h, 001h, 000h, 000h, 000h, 080h, 0F9h, 0FFh, 034h, 001h, 000h, 000h, 000h, 080h, 0FAh, 0FFh
    db 033h, 001h, 000h, 000h, 000h, 080h, 0F6h, 0FFh, 034h, 001h, 000h, 000h, 000h, 080h, 0FDh, 0FFh
    db 03Eh, 001h, 0F0h, 000h, 03Fh, 001h, 0F0h, 000h, 040h, 001h, 0F0h, 000h, 041h, 001h, 0F0h, 000h
    db 042h, 001h, 0F0h, 000h, 043h, 001h, 0F0h, 000h, 044h, 001h, 0F0h, 000h, 045h, 001h, 0F0h, 000h
    db 046h, 001h, 0F0h, 000h, 000h, 080h, 000h, 080h, 04Bh, 001h, 086h, 000h, 002h, 000h, 00Eh, 01Ch
    db 03Ah, 0FDh, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0F6h, 0FFh, 005h, 002h, 0F8h, 000h, 005h, 002h
    db 0F8h, 000h, 006h, 002h, 0F8h, 000h, 006h, 002h, 0F8h, 000h, 007h, 002h, 0F8h, 000h, 007h, 002h
    db 0F8h, 000h, 008h, 002h, 0F8h, 000h, 008h, 002h, 0F8h, 000h, 009h, 002h, 0F8h, 000h, 009h, 002h
    db 0F8h, 000h, 00Ah, 002h, 0F8h, 000h, 00Ah, 002h, 0F8h, 000h, 00Bh, 002h, 0F8h, 000h, 00Bh, 002h
    db 0F8h, 000h, 00Ch, 002h, 0F8h, 000h, 00Ch, 002h, 0F8h, 000h, 00Dh, 002h, 0F8h, 000h, 00Dh, 002h
    db 0F8h, 000h, 000h, 080h, 0F9h, 0FFh, 0F7h, 001h, 000h, 000h, 0F7h, 001h, 000h, 000h, 0F7h, 001h
    db 000h, 000h, 0F7h, 001h, 000h, 000h, 0F7h, 001h, 000h, 000h, 0F7h, 001h, 000h, 000h, 0F8h, 001h
    db 000h, 000h, 0F8h, 001h, 000h, 000h, 0F8h, 001h, 000h, 000h, 0F8h, 001h, 000h, 000h, 0F8h, 001h
    db 000h, 000h, 0F8h, 001h, 000h, 000h, 0F9h, 001h, 000h, 000h, 0F9h, 001h, 000h, 000h, 0F9h, 001h
    db 000h, 000h, 0F9h, 001h, 000h, 000h, 0F9h, 001h, 000h, 000h, 0F9h, 001h, 000h, 000h, 000h, 080h
    db 0FBh, 0FFh, 005h, 002h, 0F8h, 000h, 005h, 002h, 0F8h, 000h, 006h, 002h, 0F8h, 000h, 006h, 002h
    db 0F8h, 000h, 007h, 002h, 0F8h, 000h, 007h, 002h, 0F8h, 000h, 008h, 002h, 0F8h, 000h, 008h, 002h
    db 0F8h, 000h, 009h, 002h, 0F8h, 000h, 009h, 002h, 0F8h, 000h, 00Ah, 002h, 0F8h, 000h, 00Ah, 002h
    db 0F8h, 000h, 00Bh, 002h, 0F8h, 000h, 00Bh, 002h, 0F8h, 000h, 00Ch, 002h, 0F8h, 000h, 00Ch, 002h
    db 0F8h, 000h, 00Dh, 002h, 0F8h, 000h, 00Dh, 002h, 0F8h, 000h, 000h, 080h, 0E6h, 0FFh, 0F1h, 001h
    db 000h, 000h, 0F1h, 001h, 000h, 000h, 0F1h, 001h, 000h, 000h, 0F1h, 001h, 000h, 000h, 0F1h, 001h
    db 000h, 000h, 0F1h, 001h, 000h, 000h, 0F2h, 001h, 000h, 000h, 0F2h, 001h, 000h, 000h, 0F2h, 001h
    db 000h, 000h, 0F2h, 001h, 000h, 000h, 0F2h, 001h, 000h, 000h, 0F2h, 001h, 000h, 000h, 000h, 080h
    db 0FDh, 0FFh, 0FAh, 001h, 000h, 000h, 000h, 080h, 0FAh, 0FFh, 0FBh, 001h, 000h, 000h, 000h, 080h
    db 0FBh, 0FFh, 0FAh, 001h, 000h, 000h, 000h, 080h, 0F8h, 0FFh, 0FBh, 001h, 000h, 000h, 000h, 080h
    db 0FAh, 0FFh, 0FAh, 001h, 000h, 000h, 000h, 080h, 0F6h, 0FFh, 0FBh, 001h, 000h, 000h, 000h, 080h
    db 0F8h, 0FFh, 005h, 002h, 0F8h, 000h, 006h, 002h, 0F8h, 000h, 007h, 002h, 0F8h, 000h, 008h, 002h
    db 0F8h, 000h, 009h, 002h, 0F8h, 000h, 00Ah, 002h, 0F8h, 000h, 00Bh, 002h, 0F8h, 000h, 00Ch, 002h
    db 0F8h, 000h, 00Dh, 002h, 0F8h, 000h, 000h, 080h, 000h, 080h, 040h, 001h, 07Ah, 000h, 001h, 000h
    db 00Eh, 01Ch, 068h, 0F7h, 0FFh, 07Fh, 000h, 000h, 000h, 080h, 0E3h, 0FFh, 02Fh, 002h, 0F8h, 000h
    db 02Fh, 002h, 000h, 000h, 02Fh, 002h, 000h, 000h, 030h, 002h, 0F8h, 000h, 030h, 002h, 000h, 000h
    db 030h, 002h, 000h, 000h, 031h, 002h, 0F8h, 000h, 031h, 002h, 000h, 000h, 031h, 002h, 000h, 000h
    db 032h, 002h, 0F8h, 000h, 032h, 002h, 000h, 000h, 032h, 002h, 000h, 000h, 033h, 002h, 0F8h, 000h
    db 033h, 002h, 000h, 000h, 033h, 002h, 000h, 000h, 034h, 002h, 0F8h, 000h, 034h, 002h, 000h, 000h
    db 034h, 002h, 000h, 000h, 000h, 080h, 09Ch, 0FFh, 055h, 002h, 000h, 000h, 000h, 080h, 0FDh, 0FFh
    db 047h, 002h, 000h, 000h, 047h, 002h, 000h, 000h, 047h, 002h, 000h, 000h, 047h, 002h, 000h, 000h
    db 047h, 002h, 000h, 000h, 047h, 002h, 000h, 000h, 047h, 002h, 000h, 000h, 048h, 002h, 000h, 000h
    db 048h, 002h, 000h, 000h, 048h, 002h, 000h, 000h, 048h, 002h, 000h, 000h, 048h, 002h, 000h, 000h
    db 048h, 002h, 000h, 000h, 048h, 002h, 000h, 000h, 049h, 002h, 000h, 000h, 049h, 002h, 000h, 000h
    db 049h, 002h, 000h, 000h, 049h, 002h, 000h, 000h, 049h, 002h, 000h, 000h, 049h, 002h, 000h, 000h
    db 049h, 002h, 000h, 000h, 04Ah, 002h, 000h, 000h, 04Ah, 002h, 000h, 000h, 04Ah, 002h, 000h, 000h
    db 04Ah, 002h, 000h, 000h, 04Ah, 002h, 000h, 000h, 04Ah, 002h, 000h, 000h, 04Ah, 002h, 000h, 000h
    db 04Bh, 002h, 000h, 000h, 04Bh, 002h, 000h, 000h, 04Bh, 002h, 000h, 000h, 04Bh, 002h, 000h, 000h
    db 04Bh, 002h, 000h, 000h, 04Bh, 002h, 000h, 000h, 04Bh, 002h, 000h, 000h, 04Ch, 002h, 000h, 000h
    db 04Ch, 002h, 000h, 000h, 04Ch, 002h, 000h, 000h, 04Ch, 002h, 000h, 000h, 04Ch, 002h, 000h, 000h
    db 04Ch, 002h, 000h, 000h, 04Ch, 002h, 000h, 000h, 000h, 080h, 0F1h, 0FFh, 023h, 002h, 0F8h, 000h
    db 023h, 002h, 0F8h, 000h, 024h, 002h, 0F8h, 000h, 024h, 002h, 0F8h, 000h, 025h, 002h, 0F8h, 000h
    db 025h, 002h, 0F8h, 000h, 026h, 002h, 0F8h, 000h, 026h, 002h, 0F8h, 000h, 027h, 002h, 0F8h, 000h
    db 027h, 002h, 0F8h, 000h, 028h, 002h, 0F8h, 000h, 028h, 002h, 0F8h, 000h, 000h, 080h, 000h, 080h
    db 0E0h, 0FFh, 050h, 000h, 001h, 000h, 00Eh, 01Ch, 0CCh, 0F7h, 0FFh, 07Fh, 000h, 000h, 000h, 080h
    db 0F8h, 0FFh, 0F6h, 000h, 008h, 000h, 0F6h, 000h, 008h, 000h, 0F6h, 000h, 008h, 000h, 0F6h, 000h
    db 008h, 000h, 0F7h, 000h, 008h, 000h, 0F7h, 000h, 008h, 000h, 0F7h, 000h, 008h, 000h, 0F7h, 000h
    db 008h, 000h, 0F8h, 000h, 008h, 000h, 0F8h, 000h, 008h, 000h, 0F8h, 000h, 008h, 000h, 0F8h, 000h
    db 008h, 000h, 0F9h, 000h, 008h, 000h, 0F9h, 000h, 008h, 000h, 0F9h, 000h, 008h, 000h, 0F9h, 000h
    db 008h, 000h, 0FAh, 000h, 008h, 000h, 0FAh, 000h, 008h, 000h, 0FAh, 000h, 008h, 000h, 0FAh, 000h
    db 008h, 000h, 0FBh, 000h, 008h, 000h, 0FBh, 000h, 008h, 000h, 0FBh, 000h, 008h, 000h, 0FBh, 000h
    db 008h, 000h, 0FCh, 000h, 008h, 000h, 0FCh, 000h, 008h, 000h, 0FCh, 000h, 008h, 000h, 0FCh, 000h
    db 008h, 000h, 0FDh, 000h, 008h, 000h, 0FDh, 000h, 008h, 000h, 0FDh, 000h, 008h, 000h, 0FDh, 000h
    db 008h, 000h, 0FEh, 000h, 008h, 000h, 0FEh, 000h, 008h, 000h, 0FEh, 000h, 008h, 000h, 0FEh, 000h
    db 008h, 000h, 0FFh, 000h, 008h, 000h, 0FFh, 000h, 008h, 000h, 0FFh, 000h, 008h, 000h, 0FFh, 000h
    db 008h, 000h, 000h, 001h, 008h, 000h, 000h, 001h, 008h, 000h, 000h, 001h, 008h, 000h, 000h, 001h
    db 008h, 000h, 001h, 001h, 008h, 000h, 001h, 001h, 008h, 000h, 001h, 001h, 008h, 000h, 001h, 001h
    db 008h, 000h, 000h, 080h, 000h, 080h, 086h, 025h, 0E4h, 024h, 0FFh, 0FFh, 045h, 001h, 036h, 000h
    db 002h, 000h, 09Fh, 009h, 079h, 0FFh, 0D6h, 000h, 0F8h, 000h, 000h, 080h, 0FDh, 0FFh, 0D6h, 000h
    db 000h, 000h, 000h, 080h, 0D6h, 000h, 000h, 008h, 0D6h, 000h, 000h, 008h, 0D6h, 000h, 000h, 0F8h
    db 0D6h, 000h, 000h, 0F8h, 0D6h, 000h, 0E8h, 0F3h, 0D6h, 000h, 0E8h, 0F4h, 0D6h, 000h, 0E8h, 0F5h
    db 0D6h, 000h, 0E8h, 0F6h, 0D6h, 000h, 0E8h, 0F7h, 0D6h, 000h, 0E8h, 0F8h, 0D6h, 000h, 0E8h, 0F9h
    db 0D6h, 000h, 0E8h, 0FAh, 0D6h, 000h, 0E8h, 0FBh, 0D6h, 000h, 0E8h, 0FCh, 0D6h, 000h, 0E8h, 0FDh
    db 0D6h, 000h, 0E8h, 0FEh, 0D6h, 000h, 0E8h, 0FFh, 0FDh, 0FFh, 0D6h, 000h, 0E8h, 000h, 000h, 080h
    db 0D6h, 000h, 0E8h, 001h, 0D6h, 000h, 0E8h, 002h, 0D6h, 000h, 0E8h, 003h, 0D6h, 000h, 0E8h, 004h
    db 0D6h, 000h, 0E8h, 005h, 0D6h, 000h, 0E8h, 006h, 0D6h, 000h, 0E8h, 007h, 0D6h, 000h, 0E8h, 008h
    db 0D6h, 000h, 0E8h, 009h, 0D6h, 000h, 0E8h, 00Ah, 0D6h, 000h, 0E8h, 00Bh, 0D6h, 000h, 0E8h, 00Ch
    db 0D6h, 000h, 0E8h, 00Dh, 0FBh, 0FFh, 0D6h, 000h, 0E8h, 00Fh, 000h, 080h, 000h, 080h, 07Dh, 001h
    db 06Eh, 000h, 002h, 000h, 00Eh, 01Ch, 0F1h, 0FFh, 0B6h, 001h, 0F8h, 000h, 0B7h, 001h, 0F8h, 000h
    db 0B8h, 001h, 0F8h, 000h, 0B9h, 001h, 0F8h, 000h, 0BAh, 001h, 0F8h, 000h, 0BBh, 001h, 0F8h, 000h
    db 0BCh, 001h, 0F8h, 000h, 0BDh, 001h, 0F8h, 000h, 0BEh, 001h, 0F8h, 000h, 000h, 080h, 0FDh, 0FFh
    db 0BEh, 001h, 000h, 000h, 000h, 080h, 0D9h, 001h, 000h, 000h, 0DAh, 001h, 000h, 000h, 0DBh, 001h
    db 000h, 000h, 0DCh, 001h, 000h, 000h, 0DDh, 001h, 000h, 000h, 0DAh, 0FFh, 0DEh, 001h, 000h, 000h
    db 000h, 080h, 0F5h, 0FFh, 083h, 001h, 000h, 000h, 000h, 080h, 0D2h, 0FFh, 084h, 001h, 000h, 000h
    db 000h, 080h, 0F8h, 0FFh, 089h, 001h, 008h, 000h, 08Ah, 001h, 008h, 000h, 08Bh, 001h, 008h, 000h
    db 08Ch, 001h, 008h, 000h, 08Dh, 001h, 008h, 000h, 08Eh, 001h, 008h, 000h, 08Fh, 001h, 008h, 000h
    db 090h, 001h, 008h, 000h, 091h, 001h, 008h, 000h, 000h, 080h, 000h, 080h, 001h, 002h, 004h, 008h
    db 001h, 003h, 007h, 00Fh
    db 8 dup (000h)
    db 045h, 000h, 051h, 000h, 003h, 000h, 009h, 000h, 063h, 000h, 01Ch, 00Ch, 0FCh, 008h, 064h, 005h
    db 001h, 000h, 002h, 000h, 001h, 000h, 000h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0FFh, 0FFh
    db 473 dup (000h)
    db 0E0h, 02Ah, 0FFh, 014h, 0FFh, 0FFh, 0E0h, 0AAh, 0FFh, 014h, 0FFh, 0FFh, 0E0h, 048h, 0FFh, 000h
    db 0FFh, 0FFh, 011h, 0FFh, 0FFh, 002h, 0FFh, 0FFh, 048h, 0FFh, 0FFh, 002h, 0FFh, 0FFh, 0E0h, 0C8h
    db 0FFh, 000h, 000h, 0FFh, 091h, 0FFh, 0FFh, 002h, 000h, 0FFh, 0C8h, 0FFh, 0FFh, 002h, 000h, 0FFh
    db 0E0h, 050h, 0FFh, 004h, 0FFh, 0FFh, 02Ch, 0FFh, 0FFh, 006h, 0FFh, 0FFh, 050h, 0FFh, 0FFh, 006h
    db 0FFh, 0FFh, 0E0h, 0D0h, 0FFh, 004h, 000h, 0FFh, 0ACh, 0FFh, 0FFh, 006h, 000h, 0FFh, 0D0h, 0FFh
    db 0FFh, 006h, 000h, 0FFh, 0E0h, 04Bh, 0FFh, 008h, 0FFh, 0FFh, 01Eh, 0FFh, 0FFh, 00Ah, 0FFh, 0FFh
    db 04Bh, 0FFh, 0FFh, 00Ah, 0FFh, 0FFh, 0E0h, 0CBh, 0FFh, 008h, 000h, 0FFh, 09Eh, 0FFh, 0FFh, 00Ah
    db 000h, 0FFh, 0CBh, 0FFh, 0FFh, 00Ah, 000h, 0FFh, 0E0h, 04Dh, 0FFh, 00Ch, 0FFh, 0FFh, 01Fh, 0FFh
    db 0FFh, 00Eh, 0FFh, 0FFh, 04Dh, 0FFh, 0FFh, 00Eh, 0FFh, 0FFh, 0E0h, 0CDh, 0FFh, 00Ch, 000h, 0FFh
    db 09Fh, 0FFh, 0FFh, 00Eh, 000h, 0FFh, 0CDh, 0FFh, 0FFh, 00Eh, 000h, 0FFh, 0E0h, 01Dh, 0FFh, 010h
    db 0FFh, 0FFh, 052h, 0FFh, 0FFh, 010h, 0FFh, 0FFh, 01Dh, 0FFh, 0FFh, 012h, 0FFh, 0FFh, 0E0h, 01Ch
    db 0FFh, 012h, 0FFh, 0FFh, 0E0h, 09Dh, 0FFh, 010h, 000h, 0FFh, 0D2h, 0FFh, 0FFh, 010h, 000h, 0FFh
    db 09Dh, 0FFh, 0FFh, 012h, 000h, 0FFh, 0E0h, 09Ch, 0FFh, 012h, 000h, 0FFh, 0FFh
    db 32 dup (000h)
    db 049h, 033h, 0D5h, 033h
    db 2616 dup (000h)
    db 0FFh, 0FFh, 0FFh, 0FFh, 079h, 034h, 01Dh, 037h, 049h, 035h, 0E1h, 034h, 093h, 034h, 0B5h, 036h
    db 0FBh, 034h, 091h, 03Ah, 09Bh
    db '677Y9'
    db 013h
    db ';-;M6'
    db 0ABh, 03Ah, 0C5h, 03Ah, 0CBh, 035h, 0DFh, 03Ah, 02Fh, 035h, 0E9h, 036h, 061h, 03Bh, 081h, 036h
    db 0F9h, 03Ah, 03Bh, 038h, 0A3h, 038h, 089h
    db '8G;!8'
    db 0B9h, 037h, 07Dh, 035h, 0BDh, 038h, 08Dh, 039h, 0C1h
    db '9C:s9Q7'
    db 019h, 036h, 015h, 035h, 0B1h, 035h, 097h, 035h, 007h, 038h, 0D7h, 038h, 0F1h, 038h, 0A7h, 039h
    db 00Bh, 039h, 0DBh, 039h, 00Fh
    db ':U8]:):'
    db 0F5h, 039h, 025h, 039h, 085h, 037h, 0E5h, 035h, 0FFh
    db '5o8?936'
    db 0C7h, 034h, 0ADh, 034h, 003h, 037h, 09Fh, 037h, 07Bh, 03Bh, 0CFh
    db '6c5w:g6'
    db 0D3h, 037h, 06Bh, 037h, 0FFh, 0FFh, 079h, 034h, 01Dh, 037h, 049h, 035h, 0E1h, 034h, 093h, 034h
    db 0B5h, 036h, 0FBh, 034h, 091h, 03Ah, 09Bh
    db '677Y9'
    db 0EDh, 037h, 013h
    db ';-;M6'
    db 0ABh, 03Ah, 0C5h, 03Ah, 017h, 03Ch, 0CBh, 035h, 0DFh, 03Ah, 02Fh, 035h, 0E9h, 036h, 061h, 03Bh
    db 0AFh, 03Bh, 081h, 036h, 0F9h, 03Ah, 03Bh, 038h, 0A3h, 038h, 089h, 038h, 0C9h
    db ';G;!8'
    db 0B9h, 037h, 07Dh, 035h, 0BDh, 038h, 095h, 03Bh, 08Dh, 039h, 0C1h
    db '9C:s9Q7'
    db 0E3h, 03Bh, 019h, 036h, 015h, 035h, 0B1h, 035h, 097h, 035h, 007h, 038h, 0FDh, 03Bh, 0D7h, 038h
    db 0F1h, 038h, 0A7h, 039h, 00Bh, 039h, 0DBh, 039h, 031h, 03Ch, 00Fh
    db ':U8]:):'
    db 0F5h
    db '9K<%9'
    db 085h, 037h, 0E5h, 035h, 0FFh, 035h, 06Fh, 038h, 07Fh
    db '<?936'
    db 0C7h, 034h, 0ADh, 034h, 003h, 037h, 099h, 03Ch, 09Fh, 037h, 07Bh, 03Bh, 0CFh
    db '6c5w:e<g6'
    db 0D3h, 037h, 06Bh, 037h, 0FFh, 0FFh, 040h, 001h, 0C7h, 03Ch, 01Dh, 03Dh, 031h, 03Dh, 001h, 000h
    db 039h, 03Dh, 000h, 000h, 014h, 080h, 00Ch, 000h, 008h, 000h, 008h, 0C0h, 01Ch, 000h, 000h, 004h
    db 080h, 002h, 051h, 03Dh, 0BFh, 03Dh, 0D3h, 03Dh, 001h, 000h, 0E3h, 03Dh, 000h, 000h, 010h, 000h
    db 010h, 000h, 01Eh, 000h, 008h, 060h, 01Dh, 000h, 000h, 005h, 0C0h, 003h, 0FDh, 03Dh, 091h, 03Eh
    db 0ABh, 03Eh, 001h, 000h, 0C5h, 03Eh, 000h, 000h, 014h, 000h, 00Eh, 000h, 00Ah, 000h, 004h, 0A0h
    db 01Eh, 000h, 000h, 006h, 000h, 005h, 0D8h, 03Eh, 08Ch, 03Fh, 0A6h, 03Fh, 002h, 000h, 0B8h, 03Fh
    db 000h, 000h, 010h, 000h, 006h, 000h, 01Ah, 000h, 006h, 0C0h, 01Ch, 000h, 000h, 004h, 040h, 006h
    db 0C9h
    db '?7@K@'
    db 001h, 000h, 05Dh, 040h, 000h, 000h, 008h, 000h, 018h, 000h, 00Ch, 000h, 004h, 060h, 01Dh, 000h
    db 000h, 005h, 080h, 007h, 070h, 040h, 0EEh, 040h, 002h, 041h, 001h, 000h, 00Ah, 041h, 000h, 000h
    db 010h, 000h, 014h, 000h, 016h, 000h, 01Ah, 0A0h, 01Eh, 000h, 000h, 006h, 0C0h, 008h, 015h, 041h
    db 0A7h, 041h, 0BBh, 041h, 002h, 000h, 077h, 041h, 000h, 000h, 004h, 000h, 014h, 000h, 00Ch, 000h
    db 01Ch, 080h, 01Eh, 000h, 000h, 004h, 000h, 00Ah, 0CDh
    db 'AKB_B'
    db 001h, 000h, 071h, 042h, 000h, 000h, 002h, 000h, 004h, 000h, 002h, 000h, 00Ch, 080h, 01Ch, 000h
    db 000h, 004h, 040h, 00Bh, 08Ch, 042h, 0FCh, 042h, 016h, 043h, 003h, 000h, 01Eh, 043h, 000h, 000h
    db 020h, 000h, 018h, 000h, 004h, 000h, 008h, 0A0h, 01Fh, 0FFh, 0FFh, 005h, 080h, 00Ch, 038h, 043h
    db 0A4h, 043h, 0BEh, 043h, 002h, 000h, 0D6h, 043h, 000h, 000h, 00Ch, 000h, 014h, 000h, 01Eh, 000h
    db 00Ah, 060h, 01Dh, 000h, 000h, 006h, 0C0h, 00Dh, 0F3h, 043h, 081h, 044h, 095h, 044h, 001h, 000h
    db 09Dh, 044h, 000h, 000h, 004h, 000h, 016h, 000h, 00Ah, 000h, 01Ch, 080h, 01Bh, 000h, 000h, 004h
    db 000h, 00Fh, 0B0h
    db 'DNEbE'
    db 001h, 000h, 07Ah, 045h, 000h, 000h, 020h, 000h, 00Eh, 000h, 016h, 000h, 004h, 0C0h, 01Ch, 000h
    db 000h, 005h, 080h, 011h, 086h
    db 'E:FNF'
    db 001h, 000h, 0F8h, 045h, 000h, 000h, 00Eh, 000h, 00Eh, 000h, 018h, 000h, 006h, 060h, 01Eh, 000h
    db 000h, 006h, 0C0h, 012h
    db 'hF!G;G'
    db 002h, 000h, 0DAh, 046h, 000h, 000h, 018h, 000h, 012h, 000h, 004h, 000h, 006h, 060h, 01Eh, 000h
    db 000h, 004h, 000h, 014h, 04Bh, 047h, 008h, 048h, 028h, 048h, 002h, 000h, 0CDh, 047h, 000h, 000h
    db 00Eh, 000h, 006h, 000h, 018h, 000h, 01Ch, 060h, 01Eh, 000h, 000h, 004h, 040h, 015h, 030h, 048h
    db 0C7h, 048h, 0DBh, 048h, 001h, 000h, 092h, 048h, 000h, 000h, 020h, 000h, 014h, 000h, 018h, 000h
    db 010h, 000h, 019h, 000h, 000h, 004h, 080h, 016h, 0EBh, 048h, 085h, 049h, 099h, 049h, 002h, 000h
    db 04Dh, 049h, 000h, 000h, 010h, 000h, 014h, 000h, 01Ah, 000h, 00Eh, 000h, 01Eh, 000h, 000h, 004h
    db 0C0h, 017h, 0B1h
    db 'IGJ[J'
    db 001h, 000h, 013h, 04Ah, 000h, 000h, 01Eh, 000h, 008h, 000h, 01Eh, 000h, 016h, 0A0h, 01Eh, 000h
    db 000h, 005h, 000h, 019h, 063h, 04Ah, 0DBh, 04Ah, 0EFh, 04Ah, 001h, 000h, 0A5h, 04Ah, 000h, 000h
    db 00Eh, 000h, 016h, 000h, 020h, 000h, 014h, 000h, 01Eh, 000h, 000h, 006h, 040h, 01Ah, 0F7h, 04Ah
    db 08Dh, 04Bh, 0A1h, 04Bh, 001h, 000h, 049h, 04Bh, 000h, 000h, 00Ah, 000h, 006h, 000h, 01Ah, 000h
    db 006h, 0A0h, 01Eh, 000h, 000h, 004h, 080h, 01Bh, 0B7h
    db 'KbL|L'
    db 002h, 000h, 019h, 04Ch, 000h, 000h, 012h, 000h, 00Ch, 000h, 01Ch, 000h, 004h, 060h, 01Dh, 000h
    db 000h, 005h, 0C0h, 01Ch, 084h, 04Ch, 008h, 04Dh, 01Ch, 04Dh, 001h, 000h, 0D6h, 04Ch, 000h, 000h
    db 00Ah, 000h, 00Eh, 000h, 01Eh, 000h, 00Eh, 020h, 01Dh, 000h, 000h, 006h, 000h, 01Eh, 02Ch, 04Dh
    db 081h, 04Dh, 089h, 04Dh, 001h, 000h, 05Eh, 04Dh, 000h, 000h, 002h, 000h, 004h, 000h, 026h, 000h
    db 006h, 0C0h, 01Dh, 000h, 000h, 004h, 040h, 01Fh, 091h, 04Dh, 01Bh, 04Eh, 035h, 04Eh, 002h, 000h
    db 0D3h, 04Dh, 002h, 000h, 014h, 000h, 016h, 000h, 006h, 000h, 00Eh, 060h, 01Dh, 000h, 000h, 005h
    db 080h, 020h, 045h, 04Eh, 0D8h, 04Eh, 0ECh, 04Eh, 002h, 000h, 0A7h, 04Eh, 000h, 000h, 002h, 000h
    db 004h, 000h, 020h, 000h, 01Ch, 040h, 01Fh, 000h, 000h, 006h, 0C0h, 021h, 0F4h, 04Eh, 0B0h, 04Fh
    db 0CAh, 04Fh, 002h, 000h, 066h, 04Fh, 000h, 000h, 01Eh, 000h, 004h, 000h, 012h, 000h, 00Eh, 060h
    db 01Eh, 000h, 000h, 004h, 000h, 023h, 0DCh
    db 'O=PQP'
    db 002h, 000h, 00Eh, 050h, 000h, 000h, 020h, 000h, 00Ah, 000h, 008h, 000h, 016h, 0A0h, 01Eh, 000h
    db 000h, 005h
    db '@$aP'
    db 0E3h, 050h, 0F7h, 050h, 002h, 000h, 0A3h, 050h, 000h, 000h, 002h, 000h, 004h, 000h, 004h, 000h
    db 016h, 0C0h, 01Dh, 000h, 000h, 006h, 080h, 025h, 0FFh
    db 'PAQIQ'
    db 001h, 000h, 021h, 051h, 000h, 000h, 002h, 000h, 004h, 000h, 01Eh, 000h, 00Ah, 060h, 018h, 000h
    db 000h, 004h, 0C0h, 026h, 04Bh, 051h, 0E0h, 051h, 0FAh, 051h, 002h, 000h, 09Dh, 051h, 000h, 000h
    db 00Ch, 000h, 00Ch, 000h, 01Ah, 000h, 018h, 060h, 01Dh, 000h, 000h, 005h, 000h, 028h, 004h, 052h
    db 084h, 052h, 098h, 052h, 002h, 000h, 056h, 052h, 000h, 000h, 008h, 000h, 004h, 000h, 016h, 000h
    db 010h, 040h, 01Fh, 000h, 000h, 006h, 040h, 029h, 0A8h, 052h, 075h, 053h, 08Fh, 053h, 002h, 000h
    db 02Ah, 053h, 001h, 000h, 020h, 000h, 012h, 000h, 00Ah, 000h, 01Ah, 0A0h, 01Eh, 000h, 000h, 004h
    db 080h, 02Ah, 097h
    db 'S T4T'
    db 001h, 000h, 0E9h, 053h, 000h, 000h, 014h, 000h, 006h, 000h, 00Eh, 000h, 01Ah, 0A0h, 01Eh, 000h
    db 000h, 005h, 0C0h, 02Bh, 03Ch, 054h, 0C0h, 054h, 0D4h, 054h, 002h, 000h, 08Eh, 054h, 000h, 000h
    db 00Eh, 000h, 018h, 000h, 01Ch, 000h, 018h, 0A0h, 01Eh, 000h, 000h, 006h, 000h, 02Dh, 0E4h, 054h
    db 076h, 055h, 090h, 055h, 003h, 000h, 046h, 055h, 000h, 000h, 014h, 000h, 012h, 000h, 020h, 000h
    db 00Eh, 0E0h, 01Ah, 000h, 000h, 004h, 040h, 02Eh, 0A0h
    db 'UIVcV'
    db 003h, 000h, 012h, 056h, 000h, 000h, 014h, 000h, 00Ah, 000h, 00Ch, 000h, 006h, 060h, 01Eh, 000h
    db 000h, 005h, 080h, 02Fh, 073h, 056h, 0CCh, 056h, 0E0h, 056h, 002h, 000h, 0A5h, 056h, 000h, 000h
    db 002h, 000h, 004h, 000h, 020h, 000h, 00Eh, 080h, 01Fh, 000h, 000h, 006h, 0C0h, 030h, 0E8h
    db 'VjW~W'
    db 002h, 000h, 03Ah, 057h, 000h, 000h, 010h, 000h, 00Ah, 000h, 01Ch, 000h, 012h, 040h, 01Eh, 000h
    db 000h, 004h, 000h, 032h, 08Eh
    db 'W!X;X'
    db 003h, 000h, 0F0h, 057h, 000h, 000h, 008h, 000h, 00Eh, 000h, 020h, 000h, 01Ch, 080h, 01Eh, 000h
    db 000h, 005h
    db '@3UX'
    db 0DBh, 058h, 0EFh, 058h, 002h, 000h, 0A7h, 058h, 000h, 000h, 014h, 000h, 008h, 000h, 020h, 000h
    db 014h, 0E0h, 01Ah, 000h, 000h, 006h, 080h, 034h, 00Fh, 059h, 08Ah, 059h, 09Eh, 059h, 001h, 000h
    db 061h, 059h, 000h, 000h, 01Eh, 000h, 012h, 000h, 008h, 000h, 018h, 080h, 01Eh, 000h, 000h, 004h
    db 0C0h, 035h, 0AEh, 059h, 07Eh, 05Ah, 098h, 05Ah, 002h, 000h, 040h, 05Ah, 000h, 000h, 002h, 000h
    db 00Eh, 000h, 024h, 000h, 010h, 0C0h, 01Eh, 000h, 000h, 005h, 000h, 037h, 0A8h
    db 'Z-[A['
    db 002h, 000h, 0FAh, 05Ah, 000h, 000h, 00Eh, 000h, 010h, 000h, 006h, 000h, 004h, 0A0h, 015h, 000h
    db 000h, 006h
    db '@8Q['
    db 0C6h, 05Bh, 0D4h, 05Bh, 002h, 000h, 093h, 05Bh, 000h, 000h, 010h, 000h, 010h, 000h, 018h, 000h
    db 010h, 080h, 01Bh, 000h, 000h, 004h, 080h, 039h, 0D6h, 05Bh, 072h, 05Ch, 086h, 05Ch, 002h, 000h
    db 038h, 05Ch, 001h, 000h, 012h, 000h, 01Ah, 000h, 022h, 000h, 016h, 0C0h, 01Fh, 0FEh, 0FFh, 005h
    db 0C0h, 03Ah, 088h, 05Ch, 005h, 05Dh, 019h, 05Dh, 001h, 000h, 0DAh, 05Ch, 000h, 000h, 020h, 000h
    db 004h, 000h, 00Ch, 000h, 00Ch, 0E0h, 01Ah, 000h, 000h, 006h, 000h, 03Ch, 027h, 05Dh, 0C3h, 05Dh
    db 0DDh, 05Dh, 002h, 000h, 089h, 05Dh, 000h, 000h, 00Eh, 000h, 006h, 000h, 026h, 000h, 00Eh, 0C0h
    db 01Ch, 000h, 000h, 004h, 040h, 03Dh, 0EDh, 05Dh, 089h, 05Eh, 0A3h, 05Eh, 002h, 000h, 04Fh, 05Eh
    db 000h, 000h, 01Ah, 000h, 01Ah, 000h, 002h, 000h, 008h, 0C0h, 017h, 000h, 000h, 005h, 0C0h, 03Fh
    db 0B3h
    db '^A_U_'
    db 002h, 000h, 015h, 05Fh, 000h, 000h, 020h, 000h, 01Ah, 000h, 018h, 000h, 00Ah, 000h, 01Fh, 000h
    db 000h, 006h, 000h, 041h, 05Dh, 05Fh, 0E0h, 05Fh, 0F4h, 05Fh, 002h, 000h, 0AFh, 05Fh, 000h, 000h
    db 00Ah, 000h, 010h, 000h, 01Ah, 000h, 006h, 0A0h, 01Eh, 000h, 000h, 004h, 040h, 042h, 004h, 060h
    db 08Ah, 060h, 09Eh, 060h, 001h, 000h, 056h, 060h, 000h, 000h, 01Ah, 000h, 014h, 000h, 020h, 000h
    db 008h, 0A0h, 01Eh, 000h, 000h, 005h, 080h, 043h, 0B6h
    db '`Oaia'
    db 002h, 000h, 018h, 061h, 000h, 000h, 00Eh, 000h, 00Ah, 000h, 022h, 000h, 006h, 080h, 01Eh, 000h
    db 000h, 006h, 000h, 046h, 081h
    db 'a9bSb'
    db 002h, 000h, 0F3h, 061h, 000h, 000h, 020h, 000h, 016h, 000h, 004h, 000h, 016h, 060h, 01Dh, 000h
    db 000h, 004h
    db '@Gcb'
    db 0DAh, 062h, 0EEh, 062h, 001h, 000h, 0A5h, 062h, 000h, 000h, 010h, 000h, 006h, 000h, 010h, 000h
    db 016h, 060h, 01Dh, 000h, 000h, 005h, 080h, 048h, 0FEh, 062h, 078h, 063h, 08Ch, 063h, 002h, 000h
    db 040h, 063h, 000h, 000h, 014h, 000h, 004h, 000h, 022h, 000h, 018h, 0A0h, 01Eh, 000h, 000h, 006h
    db 0C0h, 049h, 09Ch
    db 'c(d<d'
    db 002h, 000h, 0FEh, 063h, 000h, 000h, 00Eh, 000h, 006h, 000h, 00Ch, 000h, 018h, 060h, 01Dh, 000h
    db 000h, 004h, 000h, 04Bh, 04Ch, 064h, 0C2h, 064h, 0D6h, 064h, 001h, 000h, 08Eh, 064h, 000h, 000h
    db 010h, 000h, 00Ch, 000h, 012h, 000h, 01Ah, 040h, 01Eh, 000h, 000h, 005h, 040h, 04Ch, 0E6h, 064h
    db 079h, 065h, 08Dh, 065h, 002h, 000h, 048h, 065h, 000h, 000h, 020h, 000h, 014h, 000h, 008h, 000h
    db 00Ch, 060h, 01Dh, 000h, 000h, 006h, 080h, 04Dh, 09Dh, 065h, 012h, 066h, 026h, 066h, 001h, 000h
    db 0DFh, 065h, 000h, 000h, 012h, 000h, 00Ah, 000h, 01Ch, 000h, 01Ah, 0A0h, 01Eh, 000h, 000h, 004h
    db 0C0h, 04Eh, 036h, 066h, 0F3h, 066h, 013h, 067h, 003h, 000h, 0A8h, 066h, 000h, 000h, 01Ch, 000h
    db 018h, 000h, 008h, 000h, 018h, 060h, 01Dh, 000h, 000h, 005h, 000h, 050h, 015h, 067h, 0AAh, 067h
    db 0B8h, 067h, 001h, 000h, 067h, 067h, 000h, 000h, 01Ch, 000h, 014h, 000h, 00Eh, 000h, 004h, 0A0h
    db 01Fh, 0FFh, 0FFh, 006h, 040h, 051h, 0BAh
    db 'gLh`h'
    db 002h, 000h, 01Ch, 068h, 000h, 000h, 016h, 000h, 008h, 000h, 01Ch, 000h, 016h, 060h, 01Dh, 000h
    db 000h, 004h, 080h, 052h, 070h, 068h, 0F9h, 068h, 00Dh, 069h, 001h, 000h, 0C2h, 068h, 000h, 000h
    db 022h, 000h, 016h, 000h, 004h, 000h, 018h, 0A0h, 01Eh, 000h, 000h, 005h, 0C0h, 053h, 01Dh, 069h
    db 0B3h, 069h, 0C7h, 069h, 001h, 000h, 07Fh, 069h, 000h, 000h, 01Ah, 000h, 018h, 000h, 006h, 000h
    db 006h, 0A0h, 01Eh, 000h, 000h, 006h, 040h, 056h, 0E1h, 069h, 072h, 06Ah, 086h, 06Ah, 002h, 000h
    db 043h, 06Ah, 000h, 000h, 00Ch, 000h, 006h, 000h, 006h, 000h, 01Ch, 0A0h, 01Fh, 0FFh, 0FFh, 004h
    db 080h, 057h, 08Eh, 06Ah, 0F2h, 06Ah, 006h, 06Bh, 002h, 000h, 0D0h, 06Ah, 000h, 000h, 01Ah, 000h
    db 008h, 000h, 004h, 000h, 008h, 060h, 01Dh, 000h, 000h, 005h, 0C0h, 058h, 016h, 06Bh, 0AEh, 06Bh
    db 0C8h, 06Bh, 002h, 000h, 078h, 06Bh, 000h, 000h, 01Ah, 000h, 010h, 000h, 024h, 000h, 018h, 0A0h
    db 01Eh, 000h, 000h, 006h, 000h, 05Ah, 0D8h, 06Bh, 080h, 06Ch, 094h, 06Ch, 001h, 000h, 04Ah, 06Ch
    db 000h, 000h, 014h, 000h, 01Ah, 000h, 008h, 000h, 00Ah, 0A0h, 01Eh, 000h, 000h, 004h, 040h, 05Bh
    db 0A2h
    db 'lJmdm'
    db 002h, 000h, 014h, 06Dh, 000h, 000h, 012h, 000h, 010h, 000h, 01Ah, 000h, 008h, 0A0h, 01Eh, 000h
    db 000h, 005h, 080h, 05Ch, 074h, 06Dh, 0F6h, 06Dh, 00Ah, 06Eh, 002h, 000h, 0C6h, 06Dh, 000h, 000h
    db 018h, 000h, 004h, 000h, 024h, 000h, 010h, 0A0h, 01Eh, 000h, 000h, 006h, 000h, 05Fh, 01Ah, 06Eh
    db 0A6h, 06Eh, 0C0h, 06Eh, 003h, 000h, 05Ch, 06Eh, 000h, 000h, 006h, 000h, 00Ah, 000h, 024h, 000h
    db 008h, 0A0h, 01Eh, 000h, 000h, 004h, 080h, 061h, 0C2h, 06Eh, 072h, 06Fh, 08Ch, 06Fh, 003h, 000h
    db 034h, 06Fh, 000h, 000h, 022h, 000h, 00Eh, 000h, 00Ah, 000h, 01Ah, 0A0h, 01Eh, 000h, 000h, 005h
    db 0C0h, 062h, 09Ch
    db 'o@pZp'
    db 003h, 000h, 0FEh, 06Fh, 000h, 000h, 006h, 000h, 012h, 000h, 016h, 000h, 00Eh, 060h, 01Dh, 000h
    db 000h, 006h, 000h, 064h, 074h, 070h, 01Dh, 071h, 037h, 071h, 002h, 000h, 0D6h, 070h, 000h, 000h
    db 010h, 000h, 01Ah, 000h, 00Ch, 000h, 008h, 080h, 01Eh, 000h, 000h, 004h
    db '@eGq'
    db 0CBh, 071h, 0DFh, 071h, 002h, 000h, 099h, 071h, 000h, 000h, 01Eh, 000h, 016h, 000h, 004h, 000h
    db 012h, 080h, 01Eh, 000h, 000h, 005h, 080h, 066h, 0E7h, 071h, 07Dh, 072h, 097h, 072h, 002h, 000h
    db 049h, 072h, 000h, 000h, 012h, 000h, 012h, 000h, 020h, 000h, 018h, 080h, 01Eh, 000h, 000h, 006h
    db 0C0h, 067h, 0A7h, 072h, 01Dh, 073h, 031h, 073h, 002h, 000h, 0E9h, 072h, 002h, 000h, 00Eh, 000h
    db 018h, 000h, 006h, 000h, 006h, 080h, 01Eh, 000h, 000h, 004h, 000h, 069h, 041h, 073h, 0C2h, 073h
    db 0D6h, 073h, 003h, 000h, 083h, 073h, 000h, 000h, 008h, 000h, 018h, 000h, 020h, 000h, 014h, 080h
    db 01Eh, 000h, 000h, 005h, 040h, 06Ah, 0DEh, 073h, 07Bh, 074h, 095h, 074h, 003h, 000h, 020h, 074h
    db 000h, 000h, 010h, 000h, 014h, 000h, 020h, 000h, 018h, 080h, 01Eh, 000h, 000h, 006h, 0C0h, 06Ch
    db 09Fh
    db 'tDu^u'
    db 003h, 000h, 001h, 075h, 000h, 000h, 00Ah, 000h, 018h, 000h, 022h, 000h, 014h, 060h, 01Dh, 000h
    db 000h, 004h, 000h, 06Eh, 066h, 075h, 006h, 076h, 020h, 076h, 003h, 000h, 0C8h, 075h, 000h, 000h
    db 00Ch, 000h, 016h, 000h, 024h, 000h, 010h, 060h, 01Dh, 000h, 000h, 004h, 070h, 079h, 010h, 07Ah
    db 0D4h, 079h, 0FCh, 079h, 0E8h, 079h, 084h, 079h, 0C0h, 079h, 0ACh, 079h, 098h, 079h, 0FFh, 0FFh
    db 0D0h, 000h, 040h, 001h, 030h, 000h, 020h, 001h, 000h, 001h, 0E0h, 000h, 001h, 000h, 000h, 000h
    db 000h, 000h, 070h, 000h, 070h, 000h, 020h, 000h, 030h, 000h, 050h, 000h, 002h, 000h, 000h, 000h
    db 040h, 000h, 000h, 001h, 0D0h, 000h, 0E0h, 000h, 0C0h, 000h, 060h, 000h, 003h, 000h, 000h, 000h
    db 0FFh, 0FFh, 000h, 000h, 064h, 000h, 002h, 000h, 02Ch, 001h, 001h, 000h, 0F4h, 001h, 000h, 000h
    db 0C8h, 000h, 0FFh, 0FFh, 001h, 000h, 02Ch, 001h, 000h, 000h, 0C8h, 000h, 002h, 000h, 058h, 002h
    db 001h, 000h, 02Ch, 001h, 0FFh, 0FFh, 020h, 077h, 000h, 000h, 0F9h, 03Ch, 020h, 077h, 000h, 000h
    db 00Bh, 03Dh, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 001h, 000h, 0B3h, 03Ch
    db 0FFh, 0FFh, 0FEh
    db 'INTRODUCING'
    db 00Dh, 0FEh
    db 'PLATFORMS'
    db 000h, 000h, 000h, 0B0h, 000h, 030h, 000h, 040h, 000h, 060h, 000h, 080h, 000h, 001h, 000h, 000h
    db 000h, 0A0h, 000h, 040h, 001h, 080h, 000h, 0E0h, 000h, 000h, 001h, 0B0h, 000h, 002h, 000h, 000h
    db 000h, 020h, 000h, 070h, 000h, 0A0h, 000h, 030h, 000h, 040h, 000h, 060h, 000h, 003h, 000h, 000h
    db 000h, 050h, 000h, 0F0h, 000h, 0E0h, 000h, 0D0h, 000h, 0B0h, 000h, 080h, 000h, 004h, 000h, 000h
    db 000h, 0FFh, 0FFh, 001h, 000h, 064h, 000h, 003h, 000h, 02Ch, 001h, 001h, 000h, 0F4h, 001h, 002h
    db 000h, 0C8h, 000h, 000h, 000h, 02Ch, 001h, 0FFh, 0FFh, 003h, 000h, 090h, 001h, 002h, 000h, 0C8h
    db 000h, 000h, 000h, 058h, 002h, 001h, 000h, 02Ch, 001h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 020h
    db 077h, 000h, 000h, 093h, 03Dh, 048h, 078h, 000h, 000h, 0A9h, 03Dh, 0DCh, 078h, 002h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0E4h, 076h, 002h, 000h, 0B3h, 03Ch, 06Ch, 076h, 003h, 000h, 000h, 000h, 02Dh
    db 000h, 0FFh, 0FFh, 0FEh
    db 'INTRODUCING'
    db 00Dh, 0FEh
    db 'TRIOPTERUS!'
    db 000h, 0A0h, 000h, 000h, 001h, 020h, 000h, 0E0h, 000h, 0D8h, 000h, 0B0h, 000h, 001h, 000h, 000h
    db 000h, 000h, 000h, 080h, 000h, 050h, 000h, 060h, 000h, 048h, 000h, 020h, 000h, 002h, 000h, 000h
    db 000h, 020h, 000h, 0C0h, 000h, 0A0h, 000h, 0B0h, 000h, 0A8h, 000h, 090h, 000h, 003h, 000h, 000h
    db 000h, 000h, 000h, 080h, 000h, 0E0h, 000h, 050h, 000h, 038h, 000h, 070h, 000h, 004h, 000h, 000h
    db 000h, 0D0h, 000h, 040h, 001h, 0F0h, 000h, 050h, 001h, 028h, 001h, 0E0h, 000h, 005h, 000h, 000h
    db 000h, 0FFh, 0FFh, 000h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 004h, 000h, 02Ch, 001h, 002h
    db 000h, 0C8h, 000h, 000h, 000h, 090h, 001h, 0FFh, 0FFh, 000h, 000h, 02Ch, 001h, 002h, 000h, 064h
    db 000h, 001h, 000h, 02Ch, 001h, 000h, 000h, 0F4h, 001h, 004h, 000h, 0C8h, 000h, 0FFh, 0FFh, 004h
    db 000h, 0C8h, 000h, 001h, 000h, 0F4h, 001h, 003h, 000h, 0C8h, 000h, 000h, 000h, 0BCh, 002h, 002h
    db 000h, 0C8h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db 'O> w'
    db 000h, 000h
    db 'e>Hx'
    db 000h, 000h, 07Bh, 03Eh, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0A8h, 076h, 010h, 001h
    db 080h, 000h, 000h, 000h, 002h, 000h, 0E4h, 076h, 001h, 000h, 0B3h, 03Ch, 030h, 076h, 000h, 000h
    db 0C8h, 000h, 032h, 000h, 0FFh, 0FFh, 0FEh
    db 'DINO AND THE BIRD'
    db 000h, 000h, 000h, 060h, 000h, 040h, 000h, 010h, 000h, 030h, 000h, 030h, 000h, 001h, 000h, 000h
    db 000h, 0E0h, 000h, 040h, 001h, 040h, 000h, 030h, 001h, 010h, 001h, 010h, 001h, 002h, 000h, 000h
    db 000h, 000h, 000h, 070h, 000h, 080h, 000h, 010h, 000h, 050h, 000h, 050h, 000h, 003h, 000h, 000h
    db 000h, 0F0h, 000h, 040h, 001h, 080h, 000h, 030h, 001h, 020h, 001h, 020h, 001h, 004h, 000h, 000h
    db 000h, 000h, 000h, 060h, 000h, 0C0h, 000h, 010h, 000h, 020h, 000h, 020h, 000h, 005h, 000h, 000h
    db 000h, 0C0h, 000h, 040h, 001h, 0D0h, 000h, 000h, 001h, 020h, 001h, 020h, 001h, 006h, 000h, 000h
    db 000h, 090h, 000h, 0B0h, 000h, 040h, 000h, 0A0h, 000h, 0A0h, 000h, 0A0h, 000h, 001h, 000h, 000h
    db 000h, 0FFh, 0FFh, 000h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 004h, 000h, 02Ch, 001h, 002h
    db 000h, 0C8h, 000h, 003h, 000h, 090h, 001h, 0FFh, 0FFh, 000h, 000h, 02Ch, 001h, 003h, 000h, 064h
    db 000h, 002h, 000h, 02Ch, 001h, 004h, 000h, 0F4h, 001h, 001h, 000h, 0C8h, 000h, 0FFh, 0FFh, 005h
    db 000h, 0C8h, 000h, 002h, 000h, 0F4h, 001h, 003h, 000h, 0C8h, 000h, 000h, 000h, 0BCh, 002h, 002h
    db 000h, 0C8h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db 'J? w'
    db 000h, 000h
    db '`?Hx'
    db 000h, 000h, 076h, 03Fh, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 06Ch, 076h, 005h, 000h
    db 000h, 000h, 04Bh, 000h, 030h, 076h, 000h, 000h, 090h, 001h, 032h, 000h, 0FFh, 0FFh, 0FEh
    db 'ELEVATOR ACTION'
    db 000h, 040h, 000h, 0D0h, 000h, 040h, 000h, 090h, 000h, 0B0h, 000h, 060h, 000h, 001h, 000h, 000h
    db 000h, 020h, 000h, 080h, 000h, 070h, 000h, 070h, 000h, 060h, 000h, 040h, 000h, 002h, 000h, 000h
    db 000h, 0B0h, 000h, 0F0h, 000h, 080h, 000h, 0D0h, 000h, 0C0h, 000h, 0E0h, 000h, 003h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 0C0h, 000h, 040h, 001h, 040h, 001h, 040h, 001h, 004h, 000h, 000h
    db 000h, 0FFh, 0FFh, 001h, 000h, 064h, 000h, 000h, 000h, 02Ch, 001h, 001h, 000h, 0F4h, 001h, 002h
    db 000h, 0C8h, 000h, 000h, 000h, 02Ch, 001h, 0FFh, 0FFh, 001h, 000h, 090h, 001h, 002h, 000h, 0C8h
    db 000h, 000h, 000h, 058h, 002h, 001h, 000h, 02Ch, 001h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h
    db 077h, 000h, 000h, 00Bh, 040h, 020h, 077h, 000h, 000h, 021h, 040h, 0DCh, 078h, 001h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0A8h, 076h, 010h, 001h, 0C0h, 000h, 000h, 000h, 001h, 000h, 0E4h, 076h, 000h
    db 000h, 0B3h, 03Ch, 0FFh, 0FFh, 0FEh
    db 'INTRODUCING'
    db 00Dh, 0FEh
    db 'DINO'
    db 000h, 030h, 000h, 060h, 000h, 030h, 000h, 040h, 000h, 050h, 000h, 050h, 000h, 001h, 000h, 000h
    db 000h, 0E0h, 000h, 010h, 001h, 030h, 000h, 0F0h, 000h, 000h, 001h, 000h, 001h, 002h, 000h, 000h
    db 000h, 000h, 000h, 040h, 000h, 0C0h, 000h, 0F0h, 0FFh, 010h, 000h, 030h, 000h, 003h, 000h, 000h
    db 000h, 060h, 000h, 0A0h, 000h, 0F0h, 000h, 070h, 000h, 080h, 000h, 090h, 000h, 004h, 000h, 000h
    db 000h, 000h, 001h, 040h, 001h, 0D0h, 000h, 010h, 001h, 020h, 001h, 030h, 001h, 005h, 000h, 000h
    db 000h, 0FFh, 0FFh, 004h, 000h, 064h, 000h, 000h, 000h, 02Ch, 001h, 001h, 000h, 0F4h, 001h, 003h
    db 000h, 0C8h, 000h, 002h, 000h, 02Ch, 001h, 0FFh, 0FFh, 002h, 000h, 090h, 001h, 003h, 000h, 0C8h
    db 000h, 000h, 000h, 058h, 002h, 001h, 000h, 02Ch, 001h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h
    db 077h, 000h, 000h, 0C2h, 040h, 048h, 078h, 000h, 000h, 0D8h, 040h, 0DCh, 078h, 002h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 0FEh
    db 'ZICK ZACK'
    db 000h, 080h, 000h, 0E0h, 000h, 0A0h, 000h, 090h, 000h, 0C0h, 000h, 0B0h, 000h, 001h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 030h, 000h, 030h, 001h, 020h, 001h, 020h, 001h, 002h, 000h, 000h
    db 000h, 080h, 000h, 0C0h, 000h, 040h, 000h, 090h, 000h, 0A0h, 000h, 0B0h, 000h, 003h, 000h, 000h
    db 000h, 000h, 001h, 040h, 001h, 0F0h, 000h, 030h, 001h, 020h, 001h, 010h, 001h, 004h, 000h, 000h
    db 000h, 000h, 000h, 040h, 000h, 0F0h, 000h, 020h, 000h, 020h, 000h, 020h, 000h, 005h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 0A0h, 000h, 030h, 001h, 030h, 001h, 030h, 001h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'BEWARE OF THE DINO'
    db 000h, 000h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 0FFh, 0FFh, 001h
    db 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 000h, 000h, 0C8h, 000h, 0FFh, 0FFh, 020h, 077h, 000h
    db 000h, 08Bh, 041h, 048h, 078h, 000h, 000h, 099h, 041h, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 004h, 000h, 0B3h, 03Ch, 0A8h, 076h, 010h, 001h, 0A0h, 000h, 000h, 000h, 002h
    db 000h, 0FFh, 0FFh, 070h, 000h, 0A0h, 000h, 0E0h, 000h, 090h, 000h, 080h, 000h, 080h, 000h, 001h
    db 000h, 000h, 000h, 070h, 000h, 0D0h, 000h, 030h, 000h, 0A0h, 000h, 0B0h, 000h, 0C0h, 000h, 002h
    db 000h, 000h, 000h, 090h, 000h, 0D0h, 000h, 090h, 000h, 0A0h, 000h, 0B0h, 000h, 0C0h, 000h, 003h
    db 000h, 000h, 000h, 0C0h, 000h, 030h, 001h, 0E0h, 000h, 020h, 001h, 0F0h, 000h, 000h, 001h, 004h
    db 000h, 000h, 000h, 000h, 001h, 030h, 001h, 080h, 000h, 040h, 001h, 040h, 001h, 040h, 001h, 005h
    db 000h, 000h, 000h, 0FFh, 0FFh, 000h, 000h, 064h, 000h, 003h, 000h, 02Ch, 001h, 001h, 000h, 0F4h
    db 001h, 002h, 000h, 0C8h, 000h, 003h, 000h, 02Ch, 001h, 0FFh, 0FFh, 002h, 000h, 090h, 001h, 003h
    db 000h, 0C8h, 000h, 001h, 000h, 058h, 002h, 002h, 000h, 02Ch, 001h, 000h, 000h, 064h, 000h, 0FFh
    db 0FFh, 020h, 077h, 000h, 000h, 01Fh, 042h, 0B4h, 077h, 000h, 000h, 035h, 042h, 0DCh, 078h, 002h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0A8h, 076h, 000h, 001h, 080h, 000h, 000h, 000h, 001h, 000h, 0E4h
    db 076h, 001h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 0FEh
    db 'DIVING FOR'
    db 00Dh, 0FEh
    db 'PROFESSIONALS'
    db 000h, 0C0h, 000h, 040h, 001h, 0F0h, 000h, 030h, 001h, 010h, 001h, 0E0h, 000h, 001h, 000h, 000h
    db 000h, 000h, 000h, 0A0h, 000h, 0B0h, 000h, 080h, 000h, 070h, 000h, 020h, 000h, 002h, 000h, 000h
    db 000h, 0B0h, 000h, 000h, 001h, 070h, 000h, 0C0h, 000h, 0E0h, 000h, 0F0h, 000h, 003h, 000h, 000h
    db 000h, 070h, 000h, 0A0h, 000h, 030h, 000h, 080h, 000h, 090h, 000h, 090h, 000h, 004h, 000h, 000h
    db 000h, 030h, 000h, 050h, 000h, 080h, 000h, 040h, 000h, 040h, 000h, 040h, 000h, 005h, 000h, 000h
    db 000h, 0FFh, 0FFh, 000h, 000h, 001h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 001h, 000h, 096h
    db 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 002h, 000h, 02Ch, 001h, 003h, 000h, 064h, 000h, 0FFh
    db 0FFh, 0B4h, 077h, 000h, 000h, 0DEh, 042h, 048h, 078h, 000h, 000h, 0E8h, 042h, 020h, 077h, 000h
    db 000h, 0F2h, 042h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 004h, 000h, 0B3h
    db 03Ch, 0FFh, 0FFh, 0FEh
    db 'INTRODUCING'
    db 00Dh, 0FEh
    db 'FUNNY WATER'
    db 000h, 000h, 000h, 0A0h, 000h, 0E0h, 000h, 010h, 000h, 040h, 000h, 070h, 000h, 001h, 000h, 000h
    db 000h, 000h, 000h, 080h, 000h, 040h, 000h, 030h, 000h, 050h, 000h, 070h, 000h, 002h, 000h, 000h
    db 000h, 0D0h, 000h, 040h, 001h, 080h, 000h, 020h, 001h, 000h, 001h, 0F0h, 000h, 003h, 000h, 000h
    db 000h, 0C0h, 000h, 010h, 001h, 0E0h, 000h, 000h, 001h, 0F0h, 000h, 0D0h, 000h, 004h, 000h, 000h
    db 000h, 0FFh, 0FFh, 003h, 000h, 064h, 000h, 000h, 000h, 02Ch, 001h, 001h, 000h, 0F4h, 001h, 0FFh
    db 0FFh, 002h, 000h, 090h, 001h, 003h, 000h, 0C8h, 000h, 000h, 000h, 058h, 002h, 0FFh, 0FFh, 000h
    db 000h, 058h, 002h, 001h, 000h, 02Ch, 001h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h
    db 000h
    db 'zCHx'
    db 000h, 000h, 088h, 043h, 020h, 077h, 000h, 000h, 096h, 043h, 0DCh, 078h, 001h, 000h, 000h, 000h
    db 0FFh, 0FFh, 0E4h, 076h, 000h, 000h, 0B3h, 03Ch, 030h, 076h, 000h, 000h, 090h, 001h, 032h, 000h
    db 030h, 076h, 000h, 000h, 022h, 001h, 046h, 000h, 0FFh, 0FFh, 0FEh
    db 'TWO BIRDS'
    db 00Dh, 0FEh
    db 'BUT EASY TWO FLY'
    db 000h, 000h, 000h, 050h, 000h, 070h, 000h, 030h, 000h, 038h, 000h, 040h, 000h, 001h, 000h, 000h
    db 000h, 060h, 000h, 0B0h, 000h, 0D0h, 000h, 0A0h, 000h, 080h, 000h, 090h, 000h, 002h, 000h, 000h
    db 000h, 090h, 000h, 0F0h, 000h, 030h, 000h, 0C0h, 000h, 0B0h, 000h, 0E0h, 000h, 003h, 000h, 000h
    db 000h, 090h, 000h, 0E0h, 000h, 080h, 000h, 0A0h, 000h, 0C0h, 000h, 0D0h, 000h, 004h, 000h, 000h
    db 000h, 0D0h, 000h, 020h, 001h, 0D0h, 000h, 0E0h, 000h, 0F0h, 000h, 000h, 001h, 005h, 000h, 000h
    db 000h, 000h, 000h, 030h, 000h, 0D0h, 000h, 020h, 000h, 020h, 000h, 020h, 000h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 001h, 000h, 064h, 000h, 000h, 000h, 02Ch, 001h, 003h, 000h, 0F4h, 001h, 002h
    db 000h, 0C8h, 000h, 004h, 000h, 02Ch, 001h, 0FFh, 0FFh, 002h, 000h, 090h, 001h, 003h, 000h, 0C8h
    db 000h, 000h, 000h, 058h, 002h, 004h, 000h, 02Ch, 001h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 048h
    db 078h, 000h, 000h
    db 'UD w'
    db 000h, 000h, 06Bh, 044h, 0DCh, 078h, 001h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh
    db 'ESPECIALLY FOR YOU'
    db 000h, 020h, 000h, 090h, 000h, 030h, 000h, 030h, 000h, 050h, 000h, 070h, 000h, 001h, 000h, 000h
    db 000h, 030h, 000h, 090h, 000h, 0D0h, 000h, 080h, 000h, 070h, 000h, 060h, 000h, 002h, 000h, 000h
    db 000h, 0E0h, 000h, 040h, 001h, 090h, 000h, 030h, 001h, 010h, 001h, 000h, 001h, 003h, 000h, 000h
    db 000h, 0B0h, 000h, 040h, 001h, 0D0h, 000h, 020h, 001h, 000h, 001h, 0D0h, 000h, 004h, 000h, 000h
    db 000h, 090h, 000h, 0D0h, 000h, 050h, 000h, 0A0h, 000h, 0B0h, 000h, 0C0h, 000h, 005h, 000h, 000h
    db 000h, 000h, 001h, 040h, 001h, 020h, 000h, 030h, 001h, 020h, 001h, 010h, 001h, 006h, 000h, 000h
    db 000h, 020h, 000h, 070h, 000h, 080h, 000h, 050h, 000h, 040h, 000h, 030h, 000h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 001h, 000h, 064h, 000h, 000h, 000h, 02Ch, 001h, 003h, 000h, 0F4h, 001h, 002h
    db 000h, 0C8h, 000h, 004h, 000h, 02Ch, 001h, 0FFh, 0FFh, 002h, 000h, 090h, 001h, 003h, 000h, 0C8h
    db 000h, 000h, 000h, 058h, 002h, 004h, 000h, 02Ch, 001h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 020h
    db 077h, 000h, 000h, 022h, 045h, 0B4h, 077h, 000h, 000h, 038h, 045h, 0DCh, 078h, 001h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0E4h, 076h, 000h, 000h, 0B3h, 03Ch, 06Ch, 076h, 001h, 000h, 000h, 000h, 04Bh
    db 000h, 06Ch, 076h, 003h, 000h, 000h, 000h, 032h, 000h, 0FFh, 0FFh, 0FEh
    db 'TWO TRIOPS'
    db 000h, 010h, 000h, 040h, 000h, 040h, 000h, 020h, 000h, 030h, 000h, 030h, 000h, 001h, 000h, 000h
    db 000h, 000h, 000h, 050h, 000h, 070h, 000h, 010h, 000h, 040h, 000h, 030h, 000h, 002h, 000h, 000h
    db 000h, 000h, 000h, 080h, 000h, 0A0h, 000h, 010h, 000h, 040h, 000h, 070h, 000h, 003h, 000h, 000h
    db 000h, 080h, 000h, 0C0h, 000h, 0B0h, 000h, 0B0h, 000h, 090h, 000h, 0A0h, 000h, 004h, 000h, 000h
    db 000h, 000h, 000h, 060h, 000h, 0F0h, 000h, 010h, 000h, 030h, 000h, 050h, 000h, 005h, 000h, 000h
    db 000h, 000h, 001h, 040h, 001h, 090h, 000h, 030h, 001h, 030h, 001h, 030h, 001h, 006h, 000h, 000h
    db 000h, 0B0h, 000h, 0D0h, 000h, 050h, 000h, 0C0h, 000h, 0C0h, 000h, 0C0h, 000h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'TINA TRIOP'
    db 00Dh, 0FEh, 041h, 04Eh, 044h, 00Dh, 0FEh
    db 'DONALD DONI'
    db 000h, 002h, 000h, 064h, 000h, 004h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 000h, 000h, 064h
    db 000h, 0FFh, 0FFh, 001h, 000h, 0C8h, 000h, 003h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 002h
    db 000h, 0C8h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 016h, 046h, 020h, 077h, 000h, 000h, 028h
    db 046h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 006h, 000h, 0B3h, 03Ch, 0A8h
    db 076h, 010h, 001h, 090h, 000h, 000h, 000h, 001h, 000h, 06Ch, 076h, 002h, 000h, 000h, 000h, 02Dh
    db 000h, 0FFh, 0FFh, 060h, 000h, 090h, 000h, 030h, 000h, 080h, 000h, 070h, 000h, 070h, 000h, 001h
    db 000h, 000h, 000h, 0B0h, 000h, 0F0h, 000h, 030h, 000h, 0D0h, 000h, 0C0h, 000h, 0E0h, 000h, 002h
    db 000h, 000h, 000h, 000h, 000h, 040h, 000h, 060h, 000h, 010h, 000h, 030h, 000h, 020h, 000h, 003h
    db 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 0A0h, 000h, 030h, 001h, 000h, 001h, 010h, 001h, 004h
    db 000h, 000h, 000h, 000h, 000h, 040h, 000h, 0F0h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 005h
    db 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 0F0h, 000h, 030h, 001h, 010h, 001h, 0D0h, 000h, 006h
    db 000h, 000h, 000h, 020h, 001h, 040h, 001h, 060h, 000h, 030h, 001h, 030h, 001h, 030h, 001h, 006h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'MY FIGHT AGAINST'
    db 00Dh, 0FEh
    db 'THE TRIOP'
    db 000h, 000h, 000h, 0C8h, 000h, 003h, 000h, 02Ch, 001h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 002h
    db 000h, 064h, 000h, 005h, 000h, 0C8h, 000h, 001h, 000h, 02Ch, 001h, 0FFh, 0FFh, 004h, 000h, 02Ch
    db 001h, 002h, 000h, 064h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0F7h
    db 046h, 020h, 077h, 000h, 000h, 005h, 047h, 048h, 078h, 000h, 000h, 013h, 047h, 0DCh, 078h, 005h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 006h, 000h, 0B3h, 03Ch, 06Ch, 076h, 005h, 000h, 000h
    db 000h, 037h, 000h, 0FFh, 0FFh, 000h, 000h, 050h, 000h, 030h, 000h, 010h, 000h, 040h, 000h, 030h
    db 000h, 001h, 000h, 000h, 000h, 010h, 001h, 040h, 001h, 060h, 000h, 030h, 001h, 020h, 001h, 020h
    db 001h, 002h, 000h, 000h, 000h, 000h, 000h, 080h, 000h, 060h, 000h, 010h, 000h, 060h, 000h, 070h
    db 000h, 003h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 090h, 000h, 030h, 001h, 020h, 001h, 010h
    db 001h, 004h, 000h, 000h, 000h, 020h, 000h, 060h, 000h, 0A0h, 000h, 030h, 000h, 050h, 000h, 050h
    db 000h, 005h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 0C0h, 000h, 020h, 001h, 030h, 001h, 000h
    db 001h, 006h, 000h, 000h, 000h, 000h, 000h, 040h, 000h, 0E0h, 000h, 010h, 000h, 020h, 000h, 030h
    db 000h, 006h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h, 0F0h, 000h, 030h, 001h, 010h, 001h, 0F0h
    db 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'DIAGONAL DISASTER'
    db 000h, 000h, 000h, 064h, 000h, 007h, 000h, 064h, 000h, 0FFh, 0FFh, 003h, 000h, 02Ch, 001h, 004h
    db 000h, 064h, 000h, 0FFh, 0FFh, 002h, 000h, 0C8h, 000h, 005h, 000h, 090h, 001h, 0FFh, 0FFh, 001h
    db 000h, 090h, 001h, 006h, 000h, 0F4h, 001h, 0FFh, 0FFh, 020h, 077h, 000h, 000h, 0E0h, 047h, 048h
    db 078h, 000h, 000h, 0EAh, 047h, 020h, 077h, 000h, 000h, 0F4h, 047h, 048h, 078h, 000h, 000h, 0FEh
    db 047h, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 002h, 000h, 0B3h, 03Ch, 0FFh
    db 0FFh, 0F0h, 000h, 020h, 001h, 050h, 000h, 000h, 001h, 010h, 001h, 010h, 001h, 001h, 000h, 000h
    db 000h, 0D0h, 000h, 040h, 001h, 0C0h, 000h, 020h, 001h, 000h, 001h, 0E0h, 000h, 002h, 000h, 000h
    db 000h, 000h, 000h, 040h, 000h, 0C0h, 000h, 010h, 000h, 030h, 000h, 020h, 000h, 003h, 000h, 000h
    db 000h, 050h, 000h, 0A0h, 000h, 060h, 000h, 070h, 000h, 090h, 000h, 080h, 000h, 004h, 000h, 000h
    db 000h, 000h, 000h, 030h, 000h, 060h, 000h, 010h, 000h, 020h, 000h, 020h, 000h, 005h, 000h, 000h
    db 000h, 0B0h, 000h, 0D0h, 000h, 0A0h, 000h, 0C0h, 000h, 0C0h, 000h, 0C0h, 000h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh, 044h, 04Fh, 04Eh, 027h
    db 'T DROWN'
    db 00Dh, 0FEh
    db 'THE GRANNY'
    db 000h, 002h, 000h, 064h, 000h, 001h, 000h, 0C8h, 000h, 000h, 000h, 02Ch, 001h, 0FFh, 0FFh, 001h
    db 000h, 0C8h, 000h, 004h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h
    db 000h, 0ABh, 048h, 020h, 077h, 000h, 000h, 0B9h, 048h, 0DCh, 078h, 001h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 005h, 000h, 0B3h, 03Ch, 06Ch, 076h, 001h, 000h, 000h, 000h, 02Dh, 000h, 0FFh
    db 0FFh, 000h, 000h, 090h, 000h, 030h, 000h, 010h, 000h, 030h, 000h, 070h, 000h, 001h, 000h, 000h
    db 000h, 0B0h, 000h, 040h, 001h, 030h, 000h, 020h, 001h, 000h, 001h, 0C0h, 000h, 002h, 000h, 000h
    db 000h, 000h, 000h, 060h, 000h, 090h, 000h, 010h, 000h, 030h, 000h, 040h, 000h, 003h, 000h, 000h
    db 000h, 0C0h, 000h, 040h, 001h, 090h, 000h, 000h, 001h, 0E0h, 000h, 020h, 001h, 004h, 000h, 000h
    db 000h, 000h, 000h, 090h, 000h, 0E0h, 000h, 040h, 000h, 060h, 000h, 080h, 000h, 005h, 000h, 000h
    db 000h, 0B0h, 000h, 040h, 001h, 0E0h, 000h, 030h, 001h, 010h, 001h, 0F0h, 000h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'A DAY AT WOOLWORTH'
    db 000h, 004h, 000h, 020h, 003h, 003h, 000h, 0C8h, 000h, 002h, 000h, 02Ch, 001h, 005h, 000h, 090h
    db 001h, 0FFh, 0FFh, 002h, 000h, 084h, 003h, 004h, 000h, 0C8h, 000h, 000h, 000h, 0F4h, 001h, 001h
    db 000h, 02Ch, 001h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db 'aI w'
    db 000h, 000h, 073h, 049h, 0DCh, 078h, 003h, 000h, 000h, 000h, 0FFh, 0FFh, 06Ch, 076h, 003h, 000h
    db 000h, 000h, 04Bh, 000h, 06Ch, 076h, 004h, 000h, 000h, 000h, 03Ch, 000h, 0E4h, 076h, 004h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh, 060h, 000h, 0C0h, 000h, 020h, 000h, 070h, 000h, 090h, 000h, 0B0h, 000h
    db 001h, 000h, 000h, 000h, 0B0h, 000h, 020h, 001h, 070h, 000h, 010h, 001h, 0F0h, 000h, 0C0h, 000h
    db 002h, 000h, 000h, 000h, 000h, 000h, 050h, 000h, 0A0h, 000h, 020h, 000h, 010h, 000h, 040h, 000h
    db 003h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 0E0h, 000h, 030h, 001h, 010h, 001h, 0D0h, 000h
    db 004h, 000h, 000h, 000h, 000h, 000h, 060h, 000h, 0F0h, 000h, 010h, 000h, 030h, 000h, 050h, 000h
    db 005h, 000h, 000h, 000h, 020h, 000h, 040h, 000h, 040h, 000h, 030h, 000h, 030h, 000h, 030h, 000h
    db 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'DANGER DUNGEON'
    db 000h, 003h, 000h, 02Ch, 001h, 002h, 000h, 090h, 001h, 000h, 000h, 02Ch, 001h, 004h, 000h, 090h
    db 001h, 0FFh, 0FFh, 001h, 000h, 064h, 000h, 002h, 000h, 0F4h, 001h, 000h, 000h, 02Ch, 001h, 004h
    db 000h, 058h, 002h, 0FFh, 0FFh, 020h, 077h, 000h, 000h
    db '#JHx'
    db 000h, 000h, 035h, 04Ah, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh, 000h, 000h, 0A0h, 000h, 020h, 000h, 020h, 000h, 040h, 000h, 080h, 000h
    db 001h, 000h, 000h, 000h, 000h, 000h, 060h, 000h, 070h, 000h, 010h, 000h, 030h, 000h, 050h, 000h
    db 002h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h, 050h, 000h, 0F0h, 000h, 030h, 001h, 010h, 001h
    db 003h, 000h, 000h, 000h, 0D0h, 000h, 040h, 001h, 0E0h, 000h, 020h, 001h, 010h, 001h, 0E0h, 000h
    db 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'PRETTY PLATFORMS'
    db 000h, 003h, 000h, 02Ch, 001h, 002h, 000h, 090h, 001h, 000h, 000h, 02Ch, 001h, 001h, 000h, 090h
    db 001h, 0FFh, 0FFh, 002h, 000h, 064h, 000h, 000h, 000h, 0F4h, 001h, 001h, 000h, 02Ch, 001h, 003h
    db 000h, 058h, 002h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0B7h, 04Ah, 048h, 078h, 000h, 000h, 0C9h
    db 04Ah, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 0FFh
    db 0FFh, 0C0h, 000h, 030h, 001h, 0F0h, 000h, 020h, 001h, 010h, 001h, 0E0h, 000h, 001h, 000h, 000h
    db 000h, 000h, 000h, 080h, 000h, 050h, 000h, 010h, 000h, 030h, 000h, 070h, 000h, 002h, 000h, 000h
    db 000h, 020h, 000h, 040h, 001h, 0A0h, 000h, 070h, 000h, 090h, 000h, 0E0h, 000h, 003h, 000h, 000h
    db 000h, 0A0h, 000h, 020h, 001h, 050h, 000h, 0B0h, 000h, 0D0h, 000h, 010h, 001h, 004h, 000h, 000h
    db 000h, 000h, 000h, 090h, 000h, 0F0h, 000h, 010h, 000h, 010h, 000h, 010h, 000h, 005h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'TWO TREES AND'
    db 00Dh, 0FEh
    db 'A TRICKY TUNNEL'
    db 000h, 001h, 000h, 02Ch, 001h, 003h, 000h, 090h, 001h, 002h, 000h, 02Ch, 001h, 000h, 000h, 090h
    db 001h, 0FFh, 0FFh, 003h, 000h, 064h, 000h, 002h, 000h, 0F4h, 001h, 000h, 000h, 02Ch, 001h, 001h
    db 000h, 058h, 002h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db 'iKHx'
    db 000h, 000h, 07Bh, 04Bh, 0DCh, 078h, 001h, 000h, 000h, 000h, 0FFh, 0FFh, 06Ch, 076h, 002h, 000h
    db 000h, 000h, 04Bh, 000h, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 0E4h, 076h, 004h, 000h, 0B3h, 03Ch
    db 0FFh, 0FFh, 000h, 000h, 060h, 000h, 020h, 000h, 010h, 000h, 020h, 000h, 040h, 000h, 001h, 000h
    db 000h, 000h, 0C0h, 000h, 030h, 001h, 040h, 000h, 000h, 001h, 010h, 001h, 0E0h, 000h, 002h, 000h
    db 000h, 000h, 000h, 000h, 030h, 000h, 060h, 000h, 010h, 000h, 008h, 000h, 020h, 000h, 003h, 000h
    db 000h, 000h, 070h, 000h, 010h, 001h, 090h, 000h, 0B0h, 000h, 0C0h, 000h, 080h, 000h, 004h, 000h
    db 000h, 000h, 000h, 000h, 050h, 000h, 0C0h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 005h, 000h
    db 000h, 000h, 0A0h, 000h, 040h, 001h, 0E0h, 000h, 030h, 001h, 020h, 001h, 0E0h, 000h, 006h, 000h
    db 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'MANY DESTINATIONS'
    db 000h, 000h, 000h, 02Ch, 001h, 003h, 000h, 090h, 001h, 001h, 000h, 02Ch, 001h, 005h, 000h, 090h
    db 001h, 0FFh, 0FFh, 001h, 000h, 064h, 000h, 004h, 000h, 0F4h, 001h, 005h, 000h, 02Ch, 001h, 002h
    db 000h, 058h, 002h, 0FFh, 0FFh, 002h, 000h, 090h, 001h, 005h, 000h, 0C8h, 000h, 001h, 000h, 090h
    db 001h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db ',L w'
    db 000h, 000h
    db '>LHx'
    db 000h, 000h, 050h, 04Ch, 0DCh, 078h, 001h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh, 050h, 000h, 0F0h, 000h, 030h, 000h, 0A0h, 000h, 0B0h, 000h, 0E0h, 000h
    db 001h, 000h, 000h, 000h, 000h, 000h, 090h, 000h, 090h, 000h, 010h, 000h, 030h, 000h, 080h, 000h
    db 002h, 000h, 000h, 000h, 0B0h, 000h, 040h, 001h, 090h, 000h, 030h, 001h, 020h, 001h, 000h, 001h
    db 003h, 000h, 000h, 000h, 040h, 000h, 090h, 000h, 0E0h, 000h, 050h, 000h, 060h, 000h, 080h, 000h
    db 004h, 000h, 000h, 000h, 0B0h, 000h, 000h, 001h, 0E0h, 000h, 0F0h, 000h, 0E0h, 000h, 0C0h, 000h
    db 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'BOTTLENECK I'
    db 000h, 004h, 000h, 02Ch, 001h, 002h, 000h, 090h, 001h, 003h, 000h, 02Ch, 001h, 001h, 000h, 090h
    db 001h, 0FFh, 0FFh, 002h, 000h, 064h, 000h, 000h, 000h, 0F4h, 001h, 003h, 000h, 02Ch, 001h, 004h
    db 000h, 058h, 002h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0E4h, 04Ch, 020h, 077h, 000h, 000h, 0F6h
    db 04Ch, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 06Ch, 076h, 001h, 000h, 000h, 000h, 04Bh
    db 000h, 0E4h, 076h, 002h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 040h, 000h, 0A0h, 000h, 020h, 000h, 060h
    db 000h, 070h, 000h, 080h, 000h, 001h, 000h, 000h, 000h, 0A0h, 000h, 000h, 001h, 020h, 000h, 0D0h
    db 000h, 0E0h, 000h, 0F0h, 000h, 002h, 000h, 000h, 000h, 090h, 000h, 0B0h, 000h, 0D0h, 000h, 0A0h
    db 000h, 0A0h, 000h, 0A0h, 000h, 003h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'INTRODUCING'
    db 00Dh, 0FEh
    db 'DIVING'
    db 000h, 000h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 000h, 000h, 090h, 001h, 0FFh, 0FFh, 048h
    db 078h, 000h, 000h, 073h, 04Dh, 0FFh, 0FFh, 0E4h, 076h, 002h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 020h
    db 000h, 0C0h, 000h, 030h, 000h, 040h, 000h, 060h, 000h, 0A0h, 000h, 001h, 000h, 000h, 000h, 0F0h
    db 000h, 040h, 001h, 080h, 000h, 020h, 001h, 010h, 001h, 000h, 001h, 002h, 000h, 000h, 000h, 000h
    db 000h, 080h, 000h, 090h, 000h, 010h, 000h, 030h, 000h, 070h, 000h, 003h, 000h, 000h, 000h, 040h
    db 000h, 000h, 001h, 0E0h, 000h, 0B0h, 000h, 0C0h, 000h, 070h, 000h, 004h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0FEh
    db 'WHAT A RAINY DAY'
    db 000h, 003h, 000h, 02Ch, 001h, 002h, 000h, 090h, 001h, 001h, 000h, 02Ch, 001h, 002h, 000h, 090h
    db 001h, 0FFh, 0FFh, 000h, 000h, 064h, 000h, 002h, 000h, 0F4h, 001h, 001h, 000h, 02Ch, 001h, 003h
    db 000h, 058h, 002h, 0FFh, 0FFh, 002h, 000h, 090h, 001h, 001h, 000h, 0C8h, 000h, 003h, 000h, 090h
    db 001h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0E5h, 04Dh, 020h, 077h, 000h
    db 000h, 0F7h, 04Dh, 048h, 078h, 000h, 000h, 009h, 04Eh, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh
    db 0FFh, 06Ch, 076h, 003h, 000h, 000h, 000h, 04Bh, 000h, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 0FFh
    db 0FFh, 020h, 000h, 060h, 000h, 020h, 000h, 050h, 000h, 040h, 000h, 030h, 000h, 001h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 050h, 000h, 030h, 001h, 020h, 001h, 020h, 001h, 002h, 000h, 000h
    db 000h, 050h, 000h, 090h, 000h, 090h, 000h, 060h, 000h, 070h, 000h, 080h, 000h, 003h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 0A0h, 000h, 030h, 001h, 020h, 001h, 020h, 001h, 004h, 000h, 000h
    db 000h, 050h, 000h, 0C0h, 000h, 0D0h, 000h, 080h, 000h, 070h, 000h, 0B0h, 000h, 005h, 000h, 000h
    db 000h, 0B0h, 000h, 0E0h, 000h, 060h, 000h, 0D0h, 000h, 0D0h, 000h, 0D0h, 000h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'A CAPITAL G'
    db 000h, 000h, 000h, 02Ch, 001h, 003h, 000h, 090h, 001h, 002h, 000h, 02Ch, 001h, 004h, 000h, 090h
    db 001h, 0FFh, 0FFh, 003h, 000h, 064h, 000h, 002h, 000h, 0F4h, 001h, 004h, 000h, 02Ch, 001h, 001h
    db 000h, 058h, 002h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0B4h, 04Eh, 020h, 077h, 000h, 000h, 0C6h
    db 04Eh, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h, 0B3h, 03Ch, 0FFh
    db 0FFh, 000h, 000h, 0E0h, 000h, 020h, 000h, 040h, 000h, 060h, 000h, 0D0h, 000h, 001h, 000h, 000h
    db 000h, 000h, 000h, 040h, 000h, 070h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 002h, 000h, 000h
    db 000h, 070h, 000h, 0C0h, 000h, 0B0h, 000h, 0B0h, 000h, 0A0h, 000h, 090h, 000h, 003h, 000h, 000h
    db 000h, 000h, 000h, 070h, 000h, 0F0h, 000h, 020h, 000h, 030h, 000h, 060h, 000h, 004h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 0F0h, 000h, 030h, 001h, 020h, 001h, 020h, 001h, 005h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 020h, 000h, 030h, 001h, 020h, 001h, 020h, 001h, 006h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 090h, 000h, 020h, 001h, 020h, 001h, 020h, 001h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'DINOS DEEP DUNGEON'
    db 000h, 000h, 000h, 02Ch, 001h, 002h, 000h, 090h, 001h, 003h, 000h, 02Ch, 001h, 005h, 000h, 090h
    db 001h, 0FFh, 0FFh, 005h, 000h, 064h, 000h, 000h, 000h, 0F4h, 001h, 003h, 000h, 02Ch, 001h, 001h
    db 000h, 058h, 002h, 0FFh, 0FFh, 005h, 000h, 090h, 001h, 003h, 000h, 0C8h, 000h, 004h, 000h, 090h
    db 001h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db 'zO w'
    db 000h, 000h, 08Ch, 04Fh, 048h, 078h, 000h, 000h, 09Eh, 04Fh, 0DCh, 078h, 000h, 000h, 000h, 000h
    db 0FFh, 0FFh, 0A8h, 076h, 010h, 001h, 090h, 000h, 000h, 000h, 001h, 000h, 0E4h, 076h, 002h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh, 000h, 000h, 050h, 000h, 030h, 000h, 010h, 000h, 020h, 000h, 040h, 000h
    db 001h, 000h, 000h, 000h, 070h, 000h, 0D0h, 000h, 080h, 000h, 0A0h, 000h, 0B0h, 000h, 080h, 000h
    db 002h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 0F0h, 000h, 030h, 001h, 010h, 001h, 0D0h, 000h
    db 003h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'INTRODUCING BIRD!'
    db 000h, 000h, 000h, 02Ch, 001h, 002h, 000h, 090h, 001h, 001h, 000h, 090h, 001h, 0FFh, 0FFh, 002h
    db 000h, 064h, 000h, 000h, 000h, 0F4h, 001h, 001h, 000h, 058h, 002h, 0FFh, 0FFh, 0B4h, 077h, 000h
    db 000h
    db '!PHx'
    db 000h, 000h, 02Fh, 050h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 001h, 000h
    db 0B3h, 03Ch, 030h, 076h, 000h, 000h, 090h, 001h, 01Eh, 000h, 0FFh, 0FFh, 0E0h, 000h, 040h, 001h
    db 030h, 000h, 020h, 001h, 010h, 001h, 000h, 001h, 001h, 000h, 000h, 000h, 050h, 000h, 0A0h, 000h
    db 060h, 000h, 060h, 000h, 070h, 000h, 080h, 000h, 002h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h
    db 090h, 000h, 030h, 001h, 000h, 001h, 010h, 001h, 003h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h
    db 0E0h, 000h, 030h, 001h, 010h, 001h, 0D0h, 000h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'HOW CAN I GET'
    db 00Dh, 0FEh
    db 'OVER THERE?'
    db 000h, 002h, 000h, 02Ch, 001h, 001h, 000h, 090h, 001h, 003h, 000h, 02Ch, 001h, 000h, 000h, 090h
    db 001h, 0FFh, 0FFh, 003h, 000h, 064h, 000h, 000h, 000h, 0F4h, 001h, 001h, 000h, 02Ch, 001h, 002h
    db 000h, 058h, 002h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0BFh, 050h, 020h, 077h, 000h, 000h, 0D1h
    db 050h, 0DCh, 078h, 001h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 0FFh
    db 0FFh, 020h, 000h, 050h, 000h, 020h, 000h, 040h, 000h, 030h, 000h, 030h, 000h, 001h, 000h, 000h
    db 000h, 010h, 001h, 040h, 001h, 040h, 000h, 030h, 001h, 020h, 001h, 020h, 001h, 002h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'ZICK ZACK DIVING'
    db 000h, 000h, 000h, 032h, 000h, 001h, 000h, 064h, 000h, 000h, 000h, 02Ch, 001h, 0FFh, 0FFh, 020h
    db 077h, 000h, 000h, 033h, 051h, 0FFh, 0FFh, 0FFh, 0FFh, 060h, 000h, 0E0h, 000h, 0E0h, 000h, 070h
    db 000h, 080h, 000h, 0D0h, 000h, 001h, 000h, 000h, 000h, 030h, 000h, 090h, 000h, 080h, 000h, 080h
    db 000h, 070h, 000h, 060h, 000h, 002h, 000h, 000h, 000h, 000h, 000h, 060h, 000h, 020h, 000h, 010h
    db 000h, 020h, 000h, 030h, 000h, 003h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 020h, 000h, 030h
    db 001h, 020h, 001h, 010h, 001h, 004h, 000h, 000h, 000h, 0B0h, 000h, 010h, 001h, 060h, 000h, 0C0h
    db 000h, 0F0h, 000h, 0E0h, 000h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'ANCHOR DOWN'
    db 000h, 004h, 000h, 02Ch, 001h, 003h, 000h, 090h, 001h, 001h, 000h, 02Ch, 001h, 000h, 000h, 090h
    db 001h, 0FFh, 0FFh, 001h, 000h, 064h, 000h, 000h, 000h, 0F4h, 001h, 004h, 000h, 02Ch, 001h, 002h
    db 000h, 058h, 002h, 0FFh, 0FFh, 003h, 000h, 090h, 001h, 002h, 000h, 0C8h, 000h, 000h, 000h, 090h
    db 001h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0AAh, 051h, 020h, 077h, 000h
    db 000h, 0BCh, 051h, 048h, 078h, 000h, 000h, 0CEh, 051h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh
    db 0FFh, 030h, 076h, 000h, 000h, 090h, 001h, 03Ch, 000h, 0FFh, 0FFh, 040h, 000h, 080h, 000h, 0C0h
    db 000h, 060h, 000h, 070h, 000h, 050h, 000h, 001h, 000h, 000h, 000h, 030h, 000h, 0F0h, 000h, 040h
    db 000h, 060h, 000h, 050h, 000h, 0E0h, 000h, 002h, 000h, 000h, 000h, 010h, 001h, 040h, 001h, 060h
    db 000h, 030h, 001h, 020h, 001h, 020h, 001h, 003h, 000h, 000h, 000h, 0F0h, 000h, 030h, 001h, 0C0h
    db 000h, 000h, 001h, 010h, 001h, 020h, 001h, 004h, 000h, 000h, 000h, 080h, 000h, 0A0h, 000h, 090h
    db 000h, 090h, 000h, 090h, 000h, 090h, 000h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'DIVERS DELIGHT I'
    db 000h, 002h, 000h, 0C8h, 000h, 003h, 000h, 090h, 001h, 002h, 000h, 090h, 001h, 0FFh, 0FFh, 001h
    db 000h, 0F4h, 001h, 000h, 000h, 0C8h, 000h, 003h, 000h, 058h, 002h, 0FFh, 0FFh, 020h, 077h, 000h
    db 000h
    db 'hRHx'
    db 000h, 000h, 076h, 052h, 0DCh, 078h, 001h, 000h, 000h, 000h, 0FFh, 0FFh, 06Ch, 076h, 001h, 000h
    db 000h, 000h, 04Bh, 000h, 0E4h, 076h, 004h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 030h, 000h, 090h, 000h
    db 020h, 000h, 080h, 000h, 070h, 000h, 040h, 000h, 001h, 000h, 000h, 000h, 0B0h, 000h, 000h, 001h
    db 020h, 000h, 0C0h, 000h, 0D0h, 000h, 0F0h, 000h, 002h, 000h, 000h, 000h, 0B0h, 000h, 0F0h, 000h
    db 060h, 000h, 0C0h, 000h, 0D0h, 000h, 0E0h, 000h, 003h, 000h, 000h, 000h, 050h, 000h, 090h, 000h
    db 080h, 000h, 080h, 000h, 060h, 000h, 070h, 000h, 004h, 000h, 000h, 000h, 0B0h, 000h, 010h, 001h
    db 0A0h, 000h, 0C0h, 000h, 0E0h, 000h, 000h, 001h, 005h, 000h, 000h, 000h, 020h, 000h, 080h, 000h
    db 0F0h, 000h, 060h, 000h, 050h, 000h, 030h, 000h, 006h, 000h, 000h, 000h, 0C0h, 000h, 020h, 001h
    db 0F0h, 000h, 0D0h, 000h, 0E0h, 000h, 010h, 001h, 006h, 000h, 000h, 000h, 090h, 000h, 0B0h, 000h
    db 030h, 000h, 0A0h, 000h, 0A0h, 000h, 0A0h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'UNKNOWN DESTINATION'
    db 000h, 000h, 000h, 02Ch, 001h, 003h, 000h, 090h, 001h, 002h, 000h, 02Ch, 001h, 001h, 000h, 090h
    db 001h, 0FFh, 0FFh, 004h, 000h, 064h, 000h, 002h, 000h, 0F4h, 001h, 005h, 000h, 02Ch, 001h, 006h
    db 000h, 058h, 002h, 0FFh, 0FFh, 002h, 000h, 090h, 001h, 006h, 000h, 0C8h, 000h, 005h, 000h, 090h
    db 001h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db '?S w'
    db 000h, 000h
    db 'QSHx'
    db 000h, 000h, 063h, 053h, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 007h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh, 000h, 000h, 040h, 000h, 020h, 000h, 010h, 000h, 030h, 000h, 020h, 000h
    db 001h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 020h, 000h, 030h, 001h, 010h, 001h, 020h, 001h
    db 002h, 000h, 000h, 000h, 050h, 000h, 090h, 000h, 0A0h, 000h, 070h, 000h, 060h, 000h, 080h, 000h
    db 003h, 000h, 000h, 000h, 0C0h, 000h, 000h, 001h, 0B0h, 000h, 0E0h, 000h, 0D0h, 000h, 0D0h, 000h
    db 004h, 000h, 000h, 000h, 020h, 000h, 0D0h, 000h, 0F0h, 000h, 040h, 000h, 060h, 000h, 0A0h, 000h
    db 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'BOTTLENECK'
    db 00Dh, 0FEh
    db 'FOR BEGINNERS'
    db 000h, 002h, 000h, 02Ch, 001h, 004h, 000h, 0C8h, 000h, 001h, 000h, 090h, 001h, 0FFh, 0FFh, 003h
    db 000h, 064h, 000h, 002h, 000h, 0C8h, 000h, 000h, 000h, 090h, 001h, 0FFh, 0FFh, 0B4h, 077h, 000h
    db 000h, 004h, 054h, 048h, 078h, 000h, 000h, 012h, 054h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 004h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 080h, 000h, 0C0h, 000h, 030h, 000h, 0A0h
    db 000h, 090h, 000h, 0B0h, 000h, 001h, 000h, 000h, 000h, 050h, 000h, 090h, 000h, 070h, 000h, 060h
    db 000h, 080h, 000h, 070h, 000h, 002h, 000h, 000h, 000h, 0B0h, 000h, 0F0h, 000h, 070h, 000h, 0C0h
    db 000h, 0D0h, 000h, 0E0h, 000h, 003h, 000h, 000h, 000h, 030h, 000h, 090h, 000h, 0F0h, 000h, 040h
    db 000h, 060h, 000h, 070h, 000h, 004h, 000h, 000h, 000h, 0B0h, 000h, 010h, 001h, 0F0h, 000h, 000h
    db 001h, 0F0h, 000h, 0D0h, 000h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'NEPTUNS FORK'
    db 000h, 003h, 000h, 02Ch, 001h, 004h, 000h, 090h, 001h, 001h, 000h, 02Ch, 001h, 000h, 000h, 090h
    db 001h, 0FFh, 0FFh, 002h, 000h, 064h, 000h, 004h, 000h, 0F4h, 001h, 001h, 000h, 02Ch, 001h, 003h
    db 000h, 058h, 002h, 0FFh, 0FFh, 020h, 077h, 000h, 000h, 09Ch, 054h, 048h, 078h, 000h, 000h, 0AEh
    db 054h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 06Ch, 076h, 004h, 000h, 000h, 000h, 04Bh
    db 000h, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 010h, 000h, 060h, 000h, 0D0h, 000h, 020h
    db 000h, 030h, 000h, 050h, 000h, 001h, 000h, 000h, 000h, 030h, 000h, 060h, 000h, 080h, 000h, 040h
    db 000h, 050h, 000h, 050h, 000h, 002h, 000h, 000h, 000h, 080h, 000h, 0C0h, 000h, 0B0h, 000h, 0A0h
    db 000h, 0B0h, 000h, 090h, 000h, 003h, 000h, 000h, 000h, 080h, 000h, 0C0h, 000h, 050h, 000h, 0A0h
    db 000h, 0B0h, 000h, 0B0h, 000h, 004h, 000h, 000h, 000h, 0F0h, 000h, 030h, 001h, 090h, 000h, 010h
    db 001h, 000h, 001h, 020h, 001h, 005h, 000h, 000h, 000h, 0F0h, 000h, 020h, 001h, 020h, 000h, 000h
    db 001h, 010h, 001h, 010h, 001h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'EASY!'
    db 00Dh, 0FEh, 049h, 053h, 04Eh, 027h
    db 'T IT?'
    db 000h, 001h, 000h, 02Ch, 001h, 004h, 000h, 090h, 001h, 0FFh, 0FFh, 003h, 000h, 064h, 000h, 000h
    db 000h, 0F4h, 001h, 0FFh, 0FFh, 005h, 000h, 090h, 001h, 002h, 000h, 0C8h, 000h, 0FFh, 0FFh, 0B4h
    db 077h, 000h, 000h
    db 'XU w'
    db 000h, 000h
    db 'bUHx'
    db 000h, 000h, 06Ch, 055h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 000h, 000h
    db 0B3h, 03Ch, 030h, 076h, 000h, 000h, 0DCh, 005h, 01Eh, 000h, 0FFh, 0FFh, 000h, 001h, 040h, 001h
    db 0B0h, 000h, 030h, 001h, 020h, 001h, 010h, 001h, 001h, 000h, 000h, 000h, 0C0h, 000h, 000h, 001h
    db 090h, 000h, 0D0h, 000h, 0F0h, 000h, 0E0h, 000h, 002h, 000h, 000h, 000h, 080h, 000h, 0C0h, 000h
    db 070h, 000h, 090h, 000h, 0B0h, 000h, 0A0h, 000h, 003h, 000h, 000h, 000h, 040h, 000h, 080h, 000h
    db 050h, 000h, 050h, 000h, 070h, 000h, 060h, 000h, 004h, 000h, 000h, 000h, 0A0h, 000h, 000h, 001h
    db 0F0h, 000h, 0F0h, 000h, 0D0h, 000h, 0E0h, 000h, 005h, 000h, 000h, 000h, 020h, 000h, 0A0h, 000h
    db 0E0h, 000h, 070h, 000h, 060h, 000h, 030h, 000h, 006h, 000h, 000h, 000h, 020h, 000h, 040h, 000h
    db 030h, 000h, 030h, 000h, 030h, 000h, 030h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'THE STAIRWAY'
    db 00Dh, 0FEh
    db 'TO HEAVEN'
    db 000h, 002h, 000h, 02Ch, 001h, 004h, 000h, 090h, 001h, 0FFh, 0FFh, 000h, 000h, 064h, 000h, 003h
    db 000h, 0F4h, 001h, 0FFh, 0FFh, 001h, 000h, 090h, 001h, 005h, 000h, 0C8h, 000h, 0FFh, 0FFh, 0B4h
    db 077h, 000h, 000h
    db '+V w'
    db 000h, 000h
    db '5VHx'
    db 000h, 000h, 03Fh, 056h, 0DCh, 078h, 003h, 000h, 000h, 000h, 0FFh, 0FFh, 06Ch, 076h, 005h, 000h
    db 000h, 000h, 04Bh, 000h, 0E4h, 076h, 006h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 030h, 000h, 070h, 000h
    db 020h, 000h, 060h, 000h, 040h, 000h, 050h, 000h, 001h, 000h, 000h, 000h, 0E0h, 000h, 020h, 001h
    db 020h, 000h, 0F0h, 000h, 010h, 001h, 000h, 001h, 002h, 000h, 000h, 000h, 010h, 001h, 040h, 001h
    db 070h, 000h, 020h, 001h, 020h, 001h, 020h, 001h, 003h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'DIVERS DELIGHT II'
    db 000h, 000h, 000h, 032h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 001h, 000h, 02Ch, 001h, 000h
    db 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0B8h, 056h, 020h, 077h, 000h, 000h, 0C2h
    db 056h, 0DCh, 078h, 001h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 002h, 000h, 0B3h, 03Ch, 0FFh
    db 0FFh, 0D0h, 000h, 020h, 001h, 060h, 000h, 000h, 001h, 010h, 001h, 0F0h, 000h, 001h, 000h, 000h
    db 000h, 000h, 000h, 0A0h, 000h, 070h, 000h, 010h, 000h, 030h, 000h, 090h, 000h, 002h, 000h, 000h
    db 000h, 0A0h, 000h, 020h, 001h, 0B0h, 000h, 010h, 001h, 000h, 001h, 0B0h, 000h, 003h, 000h, 000h
    db 000h, 000h, 000h, 040h, 000h, 0F0h, 000h, 010h, 000h, 030h, 000h, 020h, 000h, 004h, 000h, 000h
    db 000h, 080h, 000h, 0E0h, 000h, 0F0h, 000h, 0B0h, 000h, 0C0h, 000h, 0D0h, 000h, 005h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'A CAVE UNDER WATER'
    db 000h, 000h, 000h, 0C8h, 000h, 004h, 000h, 0F4h, 001h, 001h, 000h, 090h, 001h, 0FFh, 0FFh, 002h
    db 000h, 0F4h, 001h, 003h, 000h, 0C8h, 000h, 001h, 000h, 058h, 002h, 0FFh, 0FFh, 0B4h, 077h, 000h
    db 000h
    db 'NW w'
    db 000h, 000h, 05Ch, 057h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 06Ch, 076h, 002h, 000h
    db 000h, 000h, 04Bh, 000h, 0E4h, 076h, 001h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 000h, 000h, 090h, 000h
    db 0F0h, 000h, 020h, 000h, 030h, 000h, 070h, 000h, 001h, 000h, 000h, 000h, 000h, 001h, 040h, 001h
    db 0B0h, 000h, 030h, 001h, 010h, 001h, 020h, 001h, 002h, 000h, 000h, 000h, 000h, 000h, 060h, 000h
    db 090h, 000h, 010h, 000h, 030h, 000h, 050h, 000h, 003h, 000h, 000h, 000h, 000h, 000h, 050h, 000h
    db 030h, 000h, 010h, 000h, 030h, 000h, 020h, 000h, 004h, 000h, 000h, 000h, 010h, 001h, 040h, 001h
    db 020h, 000h, 030h, 001h, 020h, 001h, 020h, 001h, 005h, 000h, 000h, 000h, 000h, 001h, 040h, 001h
    db 070h, 000h, 030h, 001h, 010h, 001h, 020h, 001h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'THE CAPITAL I'
    db 000h, 000h, 000h, 02Ch, 001h, 003h, 000h, 090h, 001h, 002h, 000h, 090h, 001h, 0FFh, 0FFh, 001h
    db 000h, 064h, 000h, 004h, 000h, 0F4h, 001h, 0FFh, 0FFh, 001h, 000h, 0F4h, 001h, 004h, 000h, 0C8h
    db 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0FFh, 057h, 020h, 077h, 000h, 000h, 00Dh, 058h, 048h
    db 078h, 000h, 000h, 017h, 058h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0A8h, 076h, 010h
    db 001h, 070h, 000h, 000h, 000h, 002h, 000h, 06Ch, 076h, 000h, 000h, 000h, 000h, 04Bh, 000h, 0E4h
    db 076h, 000h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 020h, 000h, 060h, 000h, 020h, 000h, 040h, 000h, 030h
    db 000h, 050h, 000h, 001h, 000h, 000h, 000h, 0F0h, 000h, 020h, 001h, 020h, 000h, 010h, 001h, 000h
    db 001h, 000h, 001h, 002h, 000h, 000h, 000h, 080h, 000h, 0C0h, 000h, 070h, 000h, 0B0h, 000h, 090h
    db 000h, 0A0h, 000h, 003h, 000h, 000h, 000h, 000h, 000h, 070h, 000h, 0C0h, 000h, 040h, 000h, 050h
    db 000h, 010h, 000h, 004h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h, 0C0h, 000h, 030h, 001h, 000h
    db 001h, 010h, 001h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'GREETINGS'
    db 00Dh, 0FEh
    db 'FROM ALFRED'
    db 000h, 001h, 000h, 02Ch, 001h, 003h, 000h, 090h, 001h, 004h, 000h, 090h, 001h, 0FFh, 0FFh, 000h
    db 000h, 064h, 000h, 002h, 000h, 0F4h, 001h, 001h, 000h, 058h, 002h, 0FFh, 0FFh, 0B4h, 077h, 000h
    db 000h, 0BFh, 058h, 020h, 077h, 000h, 000h, 0CDh, 058h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 030h, 076h, 000h, 000h, 0B0h, 004h, 01Eh, 000h, 030h
    db 076h, 000h, 000h, 052h, 003h, 01Ah, 000h, 030h, 076h, 000h, 000h, 0DEh, 003h, 023h, 000h, 0FFh
    db 0FFh, 020h, 000h, 0A0h, 000h, 020h, 000h, 050h, 000h, 070h, 000h, 090h, 000h, 001h, 000h, 000h
    db 000h, 0D0h, 000h, 010h, 001h, 0B0h, 000h, 0E0h, 000h, 0F0h, 000h, 000h, 001h, 002h, 000h, 000h
    db 000h, 0A0h, 000h, 020h, 001h, 040h, 000h, 010h, 001h, 0D0h, 000h, 0B0h, 000h, 003h, 000h, 000h
    db 000h, 0F0h, 000h, 040h, 001h, 0F0h, 000h, 030h, 001h, 010h, 001h, 000h, 001h, 004h, 000h, 000h
    db 000h, 020h, 000h, 070h, 000h, 0E0h, 000h, 030h, 000h, 030h, 000h, 030h, 000h, 005h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'IN THE CAVE'
    db 000h, 003h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 001h, 000h, 090h, 001h, 0FFh, 0FFh, 002h
    db 000h, 02Ch, 001h, 003h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h
    db 000h
    db 'nYHx'
    db 000h, 000h, 07Ch, 059h, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 004h, 000h
    db 0B3h, 03Ch, 06Ch, 076h, 002h, 000h, 000h, 000h, 02Dh, 000h, 0FFh, 0FFh, 050h, 000h, 090h, 000h
    db 040h, 000h, 080h, 000h, 070h, 000h, 060h, 000h, 001h, 000h, 000h, 000h, 0B0h, 000h, 0F0h, 000h
    db 040h, 000h, 0C0h, 000h, 0D0h, 000h, 0E0h, 000h, 002h, 000h, 000h, 000h, 040h, 000h, 090h, 000h
    db 070h, 000h, 080h, 000h, 070h, 000h, 050h, 000h, 003h, 000h, 000h, 000h, 0B0h, 000h, 000h, 001h
    db 070h, 000h, 0C0h, 000h, 0E0h, 000h, 0F0h, 000h, 004h, 000h, 000h, 000h, 030h, 000h, 090h, 000h
    db 0B0h, 000h, 080h, 000h, 060h, 000h, 040h, 000h, 005h, 000h, 000h, 000h, 0B0h, 000h, 010h, 001h
    db 0B0h, 000h, 0C0h, 000h, 0E0h, 000h, 000h, 001h, 006h, 000h, 000h, 000h, 000h, 000h, 090h, 000h
    db 0F0h, 000h, 080h, 000h, 060h, 000h, 010h, 000h, 006h, 000h, 000h, 000h, 0B0h, 000h, 040h, 001h
    db 0F0h, 000h, 0D0h, 000h, 0F0h, 000h, 020h, 001h, 006h, 000h, 000h, 000h, 090h, 000h, 0B0h, 000h
    db 030h, 000h, 0A0h, 000h, 0A0h, 000h, 0A0h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'THE CHRISTMAS TREE'
    db 000h, 000h, 000h, 064h, 000h, 005h, 000h, 0C8h, 000h, 002h, 000h, 02Ch, 001h, 0FFh, 0FFh, 003h
    db 000h, 0C8h, 000h, 006h, 000h, 064h, 000h, 007h, 000h, 064h, 000h, 0FFh, 0FFh, 004h, 000h, 02Ch
    db 001h, 001h, 000h, 0C8h, 000h, 005h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 054h
    db 05Ah, 0B4h, 077h, 000h, 000h, 062h, 05Ah, 0B4h, 077h, 000h, 000h, 070h, 05Ah, 0DCh, 078h, 006h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 008h, 000h, 0B3h, 03Ch, 06Ch, 076h, 006h, 000h, 000h
    db 000h, 04Bh, 000h, 0FFh, 0FFh, 010h, 000h, 040h, 000h, 050h, 000h, 030h, 000h, 020h, 000h, 020h
    db 000h, 001h, 000h, 000h, 000h, 090h, 000h, 0C0h, 000h, 020h, 000h, 0A0h, 000h, 0B0h, 000h, 0B0h
    db 000h, 002h, 000h, 000h, 000h, 000h, 001h, 030h, 001h, 020h, 000h, 020h, 001h, 010h, 001h, 010h
    db 001h, 003h, 000h, 000h, 000h, 0D0h, 000h, 000h, 001h, 060h, 000h, 0E0h, 000h, 0F0h, 000h, 0F0h
    db 000h, 004h, 000h, 000h, 000h, 040h, 000h, 090h, 000h, 0A0h, 000h, 060h, 000h, 060h, 000h, 070h
    db 000h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'TWISTING'
    db 00Dh, 0FEh
    db 'BY THE POOL'
    db 000h, 000h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 001h
    db 000h, 0C8h, 000h, 000h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h
    db 000h, 011h, 05Bh, 048h, 078h, 000h, 000h, 01Fh, 05Bh, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 004h, 000h, 0B3h, 03Ch, 030h, 076h, 000h, 000h, 058h, 002h, 032h, 000h, 0FFh
    db 0FFh, 020h, 000h, 060h, 000h, 090h, 000h, 040h, 000h, 030h, 000h, 050h, 000h, 001h, 000h, 000h
    db 000h, 020h, 000h, 070h, 000h, 0D0h, 000h, 030h, 000h, 050h, 000h, 060h, 000h, 002h, 000h, 000h
    db 000h, 0D0h, 000h, 020h, 001h, 0D0h, 000h, 010h, 001h, 0E0h, 000h, 0E0h, 000h, 003h, 000h, 000h
    db 000h, 0E0h, 000h, 020h, 001h, 090h, 000h, 000h, 001h, 0F0h, 000h, 0F0h, 000h, 004h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'RACE FOR FUEL'
    db 000h, 000h, 000h, 064h, 000h, 002h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 001h, 000h, 064h
    db 000h, 0FFh, 0FFh, 002h, 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 000h
    db 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0A2h, 05Bh, 020h, 077h, 000h, 000h, 0B4h
    db 05Bh, 0FFh, 0FFh, 0FFh, 0FFh, 000h, 000h, 080h, 000h, 020h, 000h, 010h, 000h, 040h, 000h, 060h
    db 000h, 001h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 020h, 000h, 020h, 001h, 0E0h, 000h, 0D0h
    db 000h, 002h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 0C0h, 000h, 030h, 001h, 010h, 001h, 0F0h
    db 000h, 003h, 000h, 000h, 000h, 000h, 000h, 080h, 000h, 0C0h, 000h, 020h, 000h, 070h, 000h, 040h
    db 000h, 004h, 000h, 000h, 000h, 050h, 000h, 0F0h, 000h, 070h, 000h, 0E0h, 000h, 060h, 000h, 090h
    db 000h, 005h, 000h, 000h, 000h, 050h, 000h, 0F0h, 000h, 0F0h, 000h, 0B0h, 000h, 0A0h, 000h, 090h
    db 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'GIRLS THEY WANNA'
    db 00Dh, 0FEh
    db 'HAVE FUN'
    db 000h, 005h, 000h, 014h, 000h, 004h, 000h, 0C8h, 000h, 0FFh, 0FFh, 003h, 000h, 064h, 000h, 001h
    db 000h, 0C8h, 000h, 0FFh, 0FFh, 002h, 000h, 096h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 048h
    db 078h, 000h, 000h
    db 'T\Hx'
    db 000h, 000h
    db '^\Hx'
    db 000h, 000h, 068h, 05Ch, 0FFh, 0FFh, 0FFh, 0FFh, 000h, 000h, 030h, 000h, 080h, 000h, 0F0h, 0FFh
    db 010h, 000h, 020h, 000h, 001h, 000h, 000h, 000h, 090h, 000h, 0C0h, 000h, 060h, 000h, 0A0h, 000h
    db 0B0h, 000h, 0B0h, 000h, 002h, 000h, 000h, 000h, 010h, 001h, 040h, 001h, 060h, 000h, 030h, 001h
    db 020h, 001h, 020h, 001h, 003h, 000h, 000h, 000h, 030h, 000h, 050h, 000h, 040h, 000h, 040h, 000h
    db 040h, 000h, 040h, 000h, 004h, 000h, 000h, 000h, 0F0h, 000h, 010h, 001h, 030h, 000h, 000h, 001h
    db 000h, 001h, 000h, 001h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'TRICKY DIVING'
    db 000h, 000h, 000h, 064h, 000h, 002h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 001h
    db 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h
    db 000h, 0E9h, 05Ch, 048h, 078h, 000h, 000h, 0F7h, 05Ch, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 0E4h, 076h, 004h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 0B0h
    db 000h, 010h, 001h, 040h, 000h, 0F0h, 000h, 0E0h, 000h, 0C0h, 000h, 001h, 000h, 000h, 000h, 080h
    db 000h, 0C0h, 000h, 080h, 000h, 090h, 000h, 0A0h, 000h, 0B0h, 000h, 002h, 000h, 000h, 000h, 000h
    db 000h, 040h, 000h, 0A0h, 000h, 0F0h, 0FFh, 010h, 000h, 030h, 000h, 003h, 000h, 000h, 000h, 0E0h
    db 000h, 010h, 001h, 090h, 000h, 0F0h, 000h, 000h, 001h, 000h, 001h, 004h, 000h, 000h, 000h, 060h
    db 000h, 0A0h, 000h, 0C0h, 000h, 070h, 000h, 080h, 000h, 090h, 000h, 005h, 000h, 000h, 000h, 050h
    db 000h, 090h, 000h, 040h, 000h, 070h, 000h, 070h, 000h, 070h, 000h, 006h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0FEh
    db 'LOST IN A CAGE'
    db 000h, 004h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 003h
    db 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 002h, 000h, 02Ch
    db 001h, 000h, 000h, 064h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 099h
    db 05Dh, 020h, 077h, 000h, 000h, 0A7h, 05Dh, 048h, 078h, 000h, 000h, 0B5h, 05Dh, 0DCh, 078h, 000h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h, 0B3h, 03Ch, 06Ch, 076h, 000h, 000h, 000h
    db 000h, 02Dh, 000h, 0FFh, 0FFh, 000h, 000h, 060h, 000h, 0B0h, 000h, 010h, 000h, 030h, 000h, 040h
    db 000h, 001h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h, 0A0h, 000h, 010h, 001h, 0F0h, 000h, 030h
    db 001h, 002h, 000h, 000h, 000h, 080h, 000h, 0B0h, 000h, 090h, 000h, 090h, 000h, 0A0h, 000h, 0A0h
    db 000h, 003h, 000h, 000h, 000h, 020h, 000h, 060h, 000h, 070h, 000h, 050h, 000h, 040h, 000h, 030h
    db 000h, 004h, 000h, 000h, 000h, 0E0h, 000h, 020h, 001h, 020h, 000h, 0F0h, 000h, 010h, 001h, 000h
    db 001h, 005h, 000h, 000h, 000h, 030h, 000h, 090h, 000h, 020h, 000h, 070h, 000h, 040h, 000h, 080h
    db 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'TOWER OF BABEL'
    db 000h, 000h, 000h, 064h, 000h, 001h, 000h, 0C8h, 000h, 005h, 000h, 064h, 000h, 0FFh, 0FFh, 003h
    db 000h, 0C8h, 000h, 004h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 001h, 000h, 02Ch
    db 001h, 003h, 000h, 064h, 000h, 005h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h, 000h
    db '_^Hx'
    db 000h, 000h
    db 'm^ w'
    db 000h, 000h, 07Bh, 05Eh, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 001h, 000h
    db 0B3h, 03Ch, 030h, 076h, 000h, 000h, 0B0h, 004h, 028h, 000h, 0FFh, 0FFh, 000h, 000h, 050h, 000h
    db 020h, 000h, 040h, 000h, 030h, 000h, 010h, 000h, 001h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h
    db 020h, 000h, 030h, 001h, 000h, 001h, 010h, 001h, 002h, 000h, 000h, 000h, 000h, 000h, 050h, 000h
    db 060h, 000h, 010h, 000h, 030h, 000h, 020h, 000h, 003h, 000h, 000h, 000h, 000h, 000h, 040h, 000h
    db 0E0h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 004h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h
    db 0F0h, 000h, 030h, 001h, 010h, 001h, 0F0h, 000h, 005h, 000h, 000h, 000h, 010h, 001h, 040h, 001h
    db 090h, 000h, 030h, 001h, 030h, 001h, 030h, 001h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'NASTY TREE'
    db 000h, 000h, 000h, 064h, 000h, 004h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 001h, 000h, 064h
    db 000h, 0FFh, 0FFh, 003h, 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh
    db 0FFh, 020h, 077h, 000h, 000h
    db '!_Hx'
    db 000h, 000h, 033h, 05Fh, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh, 000h, 000h, 080h, 000h, 030h, 000h, 020h, 000h, 010h, 000h, 060h, 000h
    db 001h, 000h, 000h, 000h, 000h, 000h, 080h, 000h, 0A0h, 000h, 070h, 000h, 050h, 000h, 020h, 000h
    db 002h, 000h, 000h, 000h, 040h, 000h, 0B0h, 000h, 0F0h, 000h, 060h, 000h, 070h, 000h, 0A0h, 000h
    db 003h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 0A0h, 000h, 030h, 001h, 020h, 001h, 010h, 001h
    db 004h, 000h, 000h, 000h, 0B0h, 000h, 040h, 001h, 040h, 000h, 010h, 001h, 0F0h, 000h, 0C0h, 000h
    db 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'WODDEN PROBLEMS'
    db 000h, 000h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 004h, 000h, 064h
    db 000h, 0FFh, 0FFh, 001h, 000h, 0C8h, 000h, 000h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 0FFh
    db 0FFh, 020h, 077h, 000h, 000h, 0C0h, 05Fh, 020h, 077h, 000h, 000h, 0D2h, 05Fh, 0DCh, 078h, 001h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 004h, 000h, 0B3h, 03Ch, 06Ch, 076h, 000h, 000h, 000h
    db 000h, 037h, 000h, 0FFh, 0FFh, 010h, 000h, 0A0h, 000h, 080h, 000h, 030h, 000h, 060h, 000h, 080h
    db 000h, 001h, 000h, 000h, 000h, 000h, 000h, 0C0h, 000h, 0F0h, 000h, 0B0h, 000h, 090h, 000h, 030h
    db 000h, 002h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 0D0h, 000h, 030h, 001h, 010h, 001h, 0E0h
    db 000h, 003h, 000h, 000h, 000h, 000h, 000h, 080h, 000h, 030h, 000h, 070h, 000h, 050h, 000h, 010h
    db 000h, 004h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 060h, 000h, 020h, 001h, 020h, 001h, 020h
    db 001h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'TRIOPTERUS NASTIUS'
    db 000h, 001h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 000h, 000h, 064h
    db 000h, 0FFh, 0FFh, 002h, 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 0FFh
    db 0FFh, 0B4h, 077h, 000h, 000h
    db 'j`Hx'
    db 000h, 000h, 07Ch, 060h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 004h, 000h
    db 0B3h, 03Ch, 030h, 076h, 000h, 000h, 0E8h, 003h, 032h, 000h, 06Ch, 076h, 001h, 000h, 000h, 000h
    db 04Bh, 000h, 0FFh, 0FFh, 080h, 000h, 0E0h, 000h, 0B0h, 000h, 090h, 000h, 0D0h, 000h, 0B0h, 000h
    db 001h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 060h, 000h, 030h, 001h, 020h, 001h, 010h, 001h
    db 002h, 000h, 000h, 000h, 000h, 000h, 050h, 000h, 030h, 000h, 010h, 000h, 040h, 000h, 030h, 000h
    db 003h, 000h, 000h, 000h, 030h, 000h, 0A0h, 000h, 080h, 000h, 040h, 000h, 060h, 000h, 080h, 000h
    db 004h, 000h, 000h, 000h, 000h, 000h, 070h, 000h, 0F0h, 000h, 060h, 000h, 040h, 000h, 010h, 000h
    db 005h, 000h, 000h, 000h, 090h, 000h, 0B0h, 000h, 030h, 000h, 0A0h, 000h, 0A0h, 000h, 0A0h, 000h
    db 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'LONELY TREE'
    db 000h, 000h, 000h, 064h, 000h, 004h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 002h
    db 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 004h, 000h, 02Ch
    db 001h, 002h, 000h, 064h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db '%a w'
    db 000h, 000h
    db '3aHx'
    db 000h, 000h, 041h, 061h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h
    db 0B3h, 03Ch, 06Ch, 076h, 003h, 000h, 000h, 000h, 04Bh, 000h, 06Ch, 076h, 001h, 000h, 000h, 000h
    db 04Bh, 000h, 0FFh, 0FFh, 0E0h, 000h, 030h, 001h, 030h, 000h, 0F0h, 000h, 000h, 001h, 020h, 001h
    db 001h, 000h, 000h, 000h, 0A0h, 000h, 0D0h, 000h, 030h, 000h, 0C0h, 000h, 0B0h, 000h, 0B0h, 000h
    db 002h, 000h, 000h, 000h, 090h, 000h, 000h, 001h, 080h, 000h, 0A0h, 000h, 0C0h, 000h, 0F0h, 000h
    db 003h, 000h, 000h, 000h, 020h, 000h, 070h, 000h, 070h, 000h, 060h, 000h, 050h, 000h, 030h, 000h
    db 004h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 0E0h, 000h, 0D0h, 000h, 020h, 001h, 0F0h, 000h
    db 005h, 000h, 000h, 000h, 000h, 000h, 090h, 000h, 0E0h, 000h, 070h, 000h, 050h, 000h, 030h, 000h
    db 006h, 000h, 000h, 000h, 080h, 000h, 0A0h, 000h, 020h, 000h, 090h, 000h, 090h, 000h, 090h, 000h
    db 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'MAY THE FORCE'
    db 00Dh, 0FEh
    db 'BE WITH YOU'
    db 000h, 001h, 000h, 064h, 000h, 002h, 000h, 0C8h, 000h, 005h, 000h, 064h, 000h, 0FFh, 0FFh, 003h
    db 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 000h, 000h, 02Ch
    db 001h, 004h, 000h, 064h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 00Fh
    db 062h, 020h, 077h, 000h, 000h, 01Dh, 062h, 048h, 078h, 000h, 000h, 02Bh, 062h, 0DCh, 078h, 002h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 006h, 000h, 0B3h, 03Ch, 06Ch, 076h, 004h, 000h, 000h
    db 000h, 04Bh, 000h, 0FFh, 0FFh, 0C0h, 000h, 040h, 001h, 040h, 000h, 030h, 001h, 010h, 001h, 0D0h
    db 000h, 001h, 000h, 000h, 000h, 000h, 000h, 090h, 000h, 050h, 000h, 030h, 000h, 010h, 000h, 070h
    db 000h, 002h, 000h, 000h, 000h, 040h, 000h, 0B0h, 000h, 0E0h, 000h, 0A0h, 000h, 050h, 000h, 080h
    db 000h, 003h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 0B0h, 000h, 020h, 001h, 030h, 001h, 000h
    db 001h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'IN A SMALL CAVE'
    db 000h, 001h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 002h, 000h, 064h
    db 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 000h, 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 003h
    db 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h, 000h, 0B6h, 062h, 048h, 078h, 000h, 000h, 0CCh
    db 062h, 0DCh, 078h, 003h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 001h, 000h, 0B3h, 03Ch, 06Ch
    db 076h, 002h, 000h, 000h, 000h, 02Dh, 000h, 0FFh, 0FFh, 020h, 000h, 080h, 000h, 030h, 000h, 050h
    db 000h, 030h, 000h, 070h, 000h, 001h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 0F0h, 000h, 030h
    db 001h, 020h, 001h, 000h, 001h, 002h, 000h, 000h, 000h, 080h, 000h, 040h, 001h, 040h, 000h, 010h
    db 001h, 030h, 001h, 0C0h, 000h, 003h, 000h, 000h, 000h, 030h, 000h, 0B0h, 000h, 0E0h, 000h, 090h
    db 000h, 090h, 000h, 090h, 000h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh, 044h, 04Fh, 04Eh, 027h
    db 'T MESS WITH'
    db 00Dh, 0FEh
    db 'THE TRIOP'
    db 000h, 002h, 000h, 064h, 000h, 001h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 001h
    db 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 048h, 078h, 000h
    db 000h
    db '\cHx'
    db 000h, 000h, 06Ah, 063h, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h
    db 0B3h, 03Ch, 06Ch, 076h, 002h, 000h, 000h, 000h, 07Dh, 000h, 0FFh, 0FFh, 080h, 000h, 0C0h, 000h
    db 080h, 000h, 090h, 000h, 0A0h, 000h, 0B0h, 000h, 001h, 000h, 000h, 000h, 0C0h, 000h, 010h, 001h
    db 040h, 000h, 0F0h, 000h, 000h, 001h, 0D0h, 000h, 002h, 000h, 000h, 000h, 020h, 000h, 090h, 000h
    db 040h, 000h, 030h, 000h, 050h, 000h, 070h, 000h, 003h, 000h, 000h, 000h, 0E0h, 000h, 020h, 001h
    db 090h, 000h, 0F0h, 000h, 000h, 001h, 010h, 001h, 004h, 000h, 000h, 000h, 000h, 000h, 040h, 000h
    db 0A0h, 000h, 010h, 000h, 030h, 000h, 020h, 000h, 005h, 000h, 000h, 000h, 010h, 000h, 080h, 000h
    db 0E0h, 000h, 060h, 000h, 060h, 000h, 060h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'GRANNYS HOME'
    db 000h, 002h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 000h
    db 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h
    db 000h, 00Ch, 064h, 0B4h, 077h, 000h, 000h, 01Ah, 064h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 005h, 000h, 0B3h, 03Ch, 06Ch, 076h, 002h, 000h, 000h, 000h, 04Bh, 000h, 0FFh
    db 0FFh, 0E0h, 000h, 020h, 001h, 030h, 000h, 0F0h, 000h, 010h, 001h, 000h, 001h, 001h, 000h, 000h
    db 000h, 000h, 000h, 0A0h, 000h, 080h, 000h, 010h, 000h, 030h, 000h, 070h, 000h, 002h, 000h, 000h
    db 000h, 0F0h, 000h, 040h, 001h, 0F0h, 000h, 030h, 001h, 020h, 001h, 000h, 001h, 003h, 000h, 000h
    db 000h, 0D0h, 000h, 040h, 001h, 080h, 000h, 030h, 001h, 010h, 001h, 0E0h, 000h, 004h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'THE LITTLE CHAMBER'
    db 000h, 001h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 003h, 000h, 064h
    db 000h, 0FFh, 0FFh, 003h, 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh
    db 0FFh, 020h, 077h, 000h, 000h, 0A2h, 064h, 048h, 078h, 000h, 000h, 0B4h, 064h, 0DCh, 078h, 003h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 001h, 000h, 0B3h, 03Ch, 06Ch, 076h, 001h, 000h, 000h
    db 000h, 04Bh, 000h, 0FFh, 0FFh, 040h, 000h, 0C0h, 000h, 0E0h, 000h, 050h, 000h, 070h, 000h, 0B0h
    db 000h, 001h, 000h, 000h, 000h, 030h, 000h, 090h, 000h, 080h, 000h, 080h, 000h, 070h, 000h, 050h
    db 000h, 002h, 000h, 000h, 000h, 050h, 000h, 0A0h, 000h, 030h, 000h, 090h, 000h, 080h, 000h, 060h
    db 000h, 003h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 030h, 000h, 030h, 001h, 000h, 001h, 010h
    db 001h, 004h, 000h, 000h, 000h, 0B0h, 000h, 010h, 001h, 070h, 000h, 0C0h, 000h, 0D0h, 000h, 000h
    db 001h, 005h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 0C0h, 000h, 030h, 001h, 0E0h, 000h, 010h
    db 001h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'THE LAST TRIOPTERUS'
    db 000h, 000h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 001h
    db 000h, 0C8h, 000h, 005h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h
    db 000h
    db ']eHx'
    db 000h, 000h, 06Bh, 065h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h
    db 0B3h, 03Ch, 06Ch, 076h, 000h, 000h, 000h, 000h, 04Bh, 000h, 0FFh, 0FFh, 000h, 000h, 050h, 000h
    db 030h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 001h, 000h, 000h, 000h, 0D0h, 000h, 030h, 001h
    db 030h, 000h, 020h, 001h, 0E0h, 000h, 0F0h, 000h, 002h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h
    db 0F0h, 000h, 020h, 001h, 030h, 001h, 0E0h, 000h, 003h, 000h, 000h, 000h, 080h, 000h, 000h, 001h
    db 080h, 000h, 0B0h, 000h, 0F0h, 000h, 090h, 000h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'BIRDY IN THE CAVE'
    db 000h, 000h, 000h, 064h, 000h, 002h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 003h
    db 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 002h, 000h, 064h, 000h, 0FFh
    db 0FFh, 0B4h, 077h, 000h, 000h, 0F2h, 065h, 020h, 077h, 000h, 000h, 000h, 066h, 0DCh, 078h, 001h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 030h, 076h, 000h, 000h, 0BCh
    db 002h, 046h, 000h, 0FFh, 0FFh, 070h, 000h, 0B0h, 000h, 030h, 000h, 080h, 000h, 090h, 000h, 0A0h
    db 000h, 001h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 080h, 000h, 030h, 001h, 020h, 001h, 010h
    db 001h, 002h, 000h, 000h, 000h, 090h, 000h, 0E0h, 000h, 080h, 000h, 0B0h, 000h, 0C0h, 000h, 0D0h
    db 000h, 003h, 000h, 000h, 000h, 000h, 000h, 030h, 000h, 090h, 000h, 010h, 000h, 020h, 000h, 020h
    db 000h, 004h, 000h, 000h, 000h, 0B0h, 000h, 020h, 001h, 0E0h, 000h, 010h, 001h, 0C0h, 000h, 0E0h
    db 000h, 005h, 000h, 000h, 000h, 020h, 000h, 0A0h, 000h, 0E0h, 000h, 030h, 000h, 040h, 000h, 070h
    db 000h, 006h, 000h, 000h, 000h, 000h, 000h, 040h, 000h, 020h, 000h, 010h, 000h, 020h, 000h, 030h
    db 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'TO BE ON THE TREE'
    db 000h, 006h, 000h, 064h, 000h, 004h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 000h
    db 000h, 0C8h, 000h, 005h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 002h, 000h, 02Ch
    db 001h, 006h, 000h, 064h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 004h, 000h, 02Ch, 001h, 001h
    db 000h, 064h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0BBh, 066h, 020h
    db 077h, 000h, 000h, 0C9h, 066h, 048h, 078h, 000h, 000h, 0D7h, 066h, 048h, 078h, 000h, 000h, 0E5h
    db 066h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0FFh, 0FFh, 000h, 000h, 0B0h, 000h, 030h
    db 000h, 040h, 000h, 010h, 000h, 060h, 000h, 001h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h, 050h
    db 000h, 020h, 001h, 000h, 001h, 0F0h, 000h, 002h, 000h, 000h, 000h, 020h, 000h, 0A0h, 000h, 090h
    db 000h, 040h, 000h, 060h, 000h, 090h, 000h, 003h, 000h, 000h, 000h, 0D0h, 000h, 040h, 001h, 0E0h
    db 000h, 030h, 001h, 010h, 001h, 0E0h, 000h, 004h, 000h, 000h, 000h, 000h, 000h, 070h, 000h, 0F0h
    db 000h, 010h, 000h, 040h, 000h, 050h, 000h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'FUNNY WATER BUT'
    db 00Dh, 0FEh
    db 'YOU WILL MAKE IT'
    db 000h, 003h, 000h, 032h, 000h, 000h, 000h, 0C8h, 000h, 0FFh, 0FFh, 004h, 000h, 00Ah, 000h, 002h
    db 000h, 032h, 000h, 001h, 000h, 014h, 000h, 000h, 000h, 032h, 000h, 004h, 000h, 032h, 000h, 0FFh
    db 0FFh, 0B4h, 077h, 000h, 000h, 08Ah, 067h, 048h, 078h, 000h, 000h, 094h, 067h, 0FFh, 0FFh, 0FFh
    db 0FFh, 000h, 000h, 0A0h, 000h, 0E0h, 000h, 010h, 000h, 030h, 000h, 050h, 000h, 001h, 000h, 000h
    db 000h, 000h, 000h, 070h, 000h, 040h, 000h, 030h, 000h, 050h, 000h, 010h, 000h, 002h, 000h, 000h
    db 000h, 030h, 000h, 080h, 000h, 090h, 000h, 070h, 000h, 060h, 000h, 050h, 000h, 003h, 000h, 000h
    db 000h, 0C0h, 000h, 010h, 001h, 0E0h, 000h, 000h, 001h, 0F0h, 000h, 0D0h, 000h, 004h, 000h, 000h
    db 000h, 0C0h, 000h, 020h, 001h, 030h, 000h, 010h, 001h, 0F0h, 000h, 0D0h, 000h, 005h, 000h, 000h
    db 000h, 000h, 001h, 040h, 001h, 0A0h, 000h, 020h, 001h, 020h, 001h, 020h, 001h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'THE TRIOPS AND YOU'
    db 000h, 002h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 004h
    db 000h, 0C8h, 000h, 000h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h
    db 000h
    db '0hHx'
    db 000h, 000h, 03Eh, 068h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h
    db 0B3h, 03Ch, 06Ch, 076h, 000h, 000h, 000h, 000h, 04Bh, 000h, 0FFh, 0FFh, 060h, 000h, 0E0h, 000h
    db 0D0h, 000h, 0C0h, 000h, 0A0h, 000h, 080h, 000h, 001h, 000h, 000h, 000h, 070h, 000h, 0C0h, 000h
    db 060h, 000h, 0B0h, 000h, 0A0h, 000h, 090h, 000h, 002h, 000h, 000h, 000h, 0E0h, 000h, 020h, 001h
    db 050h, 000h, 0F0h, 000h, 000h, 001h, 010h, 001h, 003h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h
    db 0F0h, 000h, 030h, 001h, 0F0h, 000h, 010h, 001h, 004h, 000h, 000h, 000h, 000h, 000h, 060h, 000h
    db 0F0h, 000h, 020h, 000h, 020h, 000h, 020h, 000h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'THE EASY CAVE'
    db 000h, 001h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 003h, 000h, 064h
    db 000h, 0FFh, 0FFh, 003h, 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 000h
    db 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 0D1h, 068h, 020h
    db 077h, 000h, 000h, 0E3h, 068h, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 004h
    db 000h, 0B3h, 03Ch, 030h, 076h, 000h, 000h, 0B0h, 004h, 028h, 000h, 0FFh, 0FFh, 090h, 000h, 010h
    db 001h, 0F0h, 000h, 0B0h, 000h, 0D0h, 000h, 0F0h, 000h, 001h, 000h, 000h, 000h, 0A0h, 000h, 0E0h
    db 000h, 060h, 000h, 0B0h, 000h, 0C0h, 000h, 0D0h, 000h, 002h, 000h, 000h, 000h, 020h, 000h, 070h
    db 000h, 040h, 000h, 060h, 000h, 050h, 000h, 030h, 000h, 003h, 000h, 000h, 000h, 030h, 000h, 070h
    db 000h, 0F0h, 000h, 040h, 000h, 060h, 000h, 050h, 000h, 004h, 000h, 000h, 000h, 010h, 001h, 040h
    db 001h, 080h, 000h, 030h, 001h, 030h, 001h, 030h, 001h, 005h, 000h, 000h, 000h, 070h, 000h, 090h
    db 000h, 0B0h, 000h, 080h, 000h, 080h, 000h, 080h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'DINO LIKES'
    db 00Dh, 0FEh
    db 'THE LADIES'
    db 000h, 002h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 003h
    db 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 048h, 078h, 000h
    db 000h, 097h, 069h, 048h, 078h, 000h, 000h, 0A5h, 069h, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 005h, 000h, 0B3h, 03Ch, 0A8h, 076h, 010h, 001h, 080h, 000h, 000h, 000h, 001h
    db 000h, 06Ch, 076h, 000h, 000h, 000h, 000h, 04Bh, 000h, 0FFh, 0FFh, 050h, 000h, 090h, 000h, 0F0h
    db 000h, 080h, 000h, 070h, 000h, 060h, 000h, 001h, 000h, 000h, 000h, 0B0h, 000h, 010h, 001h, 0E0h
    db 000h, 0D0h, 000h, 0E0h, 000h, 000h, 001h, 002h, 000h, 000h, 000h, 030h, 000h, 080h, 000h, 090h
    db 000h, 070h, 000h, 040h, 000h, 050h, 000h, 003h, 000h, 000h, 000h, 0C0h, 000h, 020h, 001h, 090h
    db 000h, 0E0h, 000h, 010h, 001h, 000h, 001h, 004h, 000h, 000h, 000h, 040h, 000h, 090h, 000h, 050h
    db 000h, 080h, 000h, 070h, 000h, 050h, 000h, 005h, 000h, 000h, 000h, 090h, 000h, 0D0h, 000h, 030h
    db 000h, 0B0h, 000h, 0B0h, 000h, 0B0h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'TOWER OF ATLANTIS'
    db 000h, 000h, 000h, 00Ah, 000h, 002h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 001h
    db 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h
    db 000h
    db 'VjHx'
    db 000h, 000h, 064h, 06Ah, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh, 000h, 000h, 040h, 000h, 060h, 000h, 0F0h, 0FFh, 010h, 000h, 030h, 000h
    db 001h, 000h, 000h, 000h, 0A0h, 000h, 0F0h, 000h, 070h, 000h, 0C0h, 000h, 0B0h, 000h, 0E0h, 000h
    db 002h, 000h, 000h, 000h, 010h, 000h, 090h, 000h, 0E0h, 000h, 020h, 000h, 030h, 000h, 060h, 000h
    db 003h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 050h, 000h, 010h, 001h, 010h, 001h, 010h, 001h
    db 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'BIG CAVE'
    db 000h, 001h, 000h, 064h, 000h, 002h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 000h
    db 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 0FFh, 0FFh, 048h, 078h, 000h, 000h, 0DAh, 06Ah, 020h
    db 077h, 000h, 000h, 0E8h, 06Ah, 0DCh, 078h, 001h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h
    db 000h, 0B3h, 03Ch, 030h, 076h, 000h, 000h, 090h, 001h, 032h, 000h, 0FFh, 0FFh, 020h, 000h, 090h
    db 000h, 020h, 000h, 030h, 000h, 040h, 000h, 070h, 000h, 001h, 000h, 000h, 000h, 0F0h, 000h, 040h
    db 001h, 040h, 000h, 030h, 001h, 020h, 001h, 000h, 001h, 002h, 000h, 000h, 000h, 000h, 000h, 040h
    db 000h, 0E0h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 003h, 000h, 000h, 000h, 050h, 000h, 0B0h
    db 000h, 060h, 000h, 060h, 000h, 070h, 000h, 080h, 000h, 004h, 000h, 000h, 000h, 0F0h, 000h, 040h
    db 001h, 0F0h, 000h, 000h, 001h, 030h, 001h, 020h, 001h, 005h, 000h, 000h, 000h, 0C0h, 000h, 000h
    db 001h, 0B0h, 000h, 0E0h, 000h, 0E0h, 000h, 0E0h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'DIVING FUN'
    db 000h, 000h, 000h, 064h, 000h, 004h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 001h
    db 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 004h, 000h, 02Ch
    db 001h, 000h, 000h, 064h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h, 084h
    db 06Bh, 020h, 077h, 000h, 000h, 092h, 06Bh, 048h, 078h, 000h, 000h, 0A0h, 06Bh, 0DCh, 078h, 003h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h, 0B3h, 03Ch, 06Ch, 076h, 000h, 000h, 000h
    db 000h, 04Bh, 000h, 0FFh, 0FFh, 000h, 001h, 040h, 001h, 0E0h, 000h, 010h, 001h, 030h, 001h, 020h
    db 001h, 001h, 000h, 000h, 000h, 000h, 001h, 030h, 001h, 020h, 000h, 020h, 001h, 010h, 001h, 000h
    db 001h, 002h, 000h, 000h, 000h, 050h, 000h, 090h, 000h, 020h, 000h, 080h, 000h, 070h, 000h, 060h
    db 000h, 003h, 000h, 000h, 000h, 000h, 000h, 050h, 000h, 0F0h, 000h, 030h, 000h, 040h, 000h, 010h
    db 000h, 004h, 000h, 000h, 000h, 070h, 000h, 0D0h, 000h, 0F0h, 000h, 080h, 000h, 0B0h, 000h, 0A0h
    db 000h, 005h, 000h, 000h, 000h, 0F0h, 000h, 010h, 001h, 070h, 000h, 000h, 001h, 000h, 001h, 000h
    db 001h, 006h, 000h, 000h, 000h, 030h, 000h, 050h, 000h, 070h, 000h, 040h, 000h, 040h, 000h, 040h
    db 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'TREES ON THE TOP'
    db 000h, 002h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 003h, 000h, 064h
    db 000h, 0FFh, 0FFh, 004h, 000h, 0C8h, 000h, 001h, 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 000h
    db 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db '\lHx'
    db 000h, 000h, 06Eh, 06Ch, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 005h, 000h
    db 0B3h, 03Ch, 0E4h, 076h, 006h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 020h, 000h, 060h, 000h, 030h, 000h
    db 030h, 000h, 040h, 000h, 050h, 000h, 001h, 000h, 000h, 000h, 0F0h, 000h, 040h, 001h, 020h, 000h
    db 030h, 001h, 020h, 001h, 000h, 001h, 002h, 000h, 000h, 000h, 0C0h, 000h, 000h, 001h, 060h, 000h
    db 0E0h, 000h, 0F0h, 000h, 0D0h, 000h, 003h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 0B0h, 000h
    db 030h, 001h, 010h, 001h, 020h, 001h, 004h, 000h, 000h, 000h, 000h, 000h, 0E0h, 000h, 0F0h, 000h
    db 010h, 000h, 040h, 000h, 060h, 000h, 005h, 000h, 000h, 000h, 070h, 000h, 0B0h, 000h, 0A0h, 000h
    db 090h, 000h, 0A0h, 000h, 080h, 000h, 006h, 000h, 000h, 000h, 020h, 000h, 050h, 000h, 090h, 000h
    db 030h, 000h, 030h, 000h, 030h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'EASY TRIOP'
    db 000h, 003h, 000h, 064h, 000h, 001h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 000h
    db 000h, 0C8h, 000h, 005h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 001h, 000h, 02Ch
    db 001h, 004h, 000h, 064h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db ' m w'
    db 000h, 000h
    db '.mHx'
    db 000h, 000h, 03Ch, 06Dh, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 006h, 000h
    db 0B3h, 03Ch, 06Ch, 076h, 004h, 000h, 000h, 000h, 04Bh, 000h, 0FFh, 0FFh, 020h, 000h, 090h, 000h
    db 020h, 000h, 030h, 000h, 040h, 000h, 070h, 000h, 001h, 000h, 000h, 000h, 0F0h, 000h, 030h, 001h
    db 020h, 000h, 020h, 001h, 010h, 001h, 000h, 001h, 002h, 000h, 000h, 000h, 040h, 000h, 090h, 000h
    db 090h, 000h, 050h, 000h, 080h, 000h, 070h, 000h, 003h, 000h, 000h, 000h, 0F0h, 000h, 030h, 001h
    db 0A0h, 000h, 000h, 001h, 010h, 001h, 020h, 001h, 004h, 000h, 000h, 000h, 020h, 000h, 0A0h, 000h
    db 0F0h, 000h, 030h, 000h, 050h, 000h, 080h, 000h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'DUNGEON DIVERS'
    db 000h, 001h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 000h
    db 000h, 0C8h, 000h, 004h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 002h, 000h, 064h, 000h, 0FFh
    db 0FFh, 048h, 078h, 000h, 000h, 0D6h, 06Dh, 020h, 077h, 000h, 000h, 0E4h, 06Dh, 0DCh, 078h, 004h
    db 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 002h, 000h, 0B3h, 03Ch, 06Ch, 076h, 000h, 000h, 000h
    db 000h, 04Bh, 000h, 0FFh, 0FFh, 000h, 000h, 040h, 000h, 070h, 000h, 0F0h, 0FFh, 010h, 000h, 020h
    db 000h, 001h, 000h, 000h, 000h, 010h, 001h, 040h, 001h, 070h, 000h, 050h, 001h, 030h, 001h, 020h
    db 001h, 002h, 000h, 000h, 000h, 070h, 000h, 0D0h, 000h, 0F0h, 000h, 080h, 000h, 0A0h, 000h, 0B0h
    db 000h, 003h, 000h, 000h, 000h, 090h, 000h, 0D0h, 000h, 020h, 000h, 0C0h, 000h, 0B0h, 000h, 0A0h
    db 000h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'STONE I ANAPOLIS'
    db 000h, 000h, 000h, 00Ah, 000h, 003h, 000h, 032h, 000h, 001h, 000h, 0C8h, 000h, 0FFh, 0FFh, 003h
    db 000h, 014h, 000h, 001h, 000h, 032h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 001h, 000h, 028h
    db 000h, 002h, 000h, 032h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 002h, 000h, 01Eh, 000h, 000h
    db 000h, 032h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h, 000h
    db 'nn w'
    db 000h, 000h
    db '|n w'
    db 000h, 000h, 08Ah, 06Eh, 020h, 077h, 000h, 000h, 098h, 06Eh, 0FFh, 0FFh, 0FFh, 0FFh, 000h, 000h
    db 040h, 000h, 040h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 001h, 000h, 000h, 000h, 050h, 000h
    db 090h, 000h, 080h, 000h, 080h, 000h, 070h, 000h, 060h, 000h, 002h, 000h, 000h, 000h, 000h, 000h
    db 040h, 000h, 0C0h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 003h, 000h, 000h, 000h, 0B0h, 000h
    db 010h, 001h, 030h, 000h, 0C0h, 000h, 0D0h, 000h, 0F0h, 000h, 004h, 000h, 000h, 000h, 000h, 001h
    db 040h, 001h, 090h, 000h, 050h, 001h, 030h, 001h, 010h, 001h, 005h, 000h, 000h, 000h, 0B0h, 000h
    db 0D0h, 000h, 0B0h, 000h, 0C0h, 000h, 0C0h, 000h, 0C0h, 000h, 006h, 000h, 000h, 000h, 0B0h, 000h
    db 020h, 001h, 0F0h, 000h, 0F0h, 000h, 0F0h, 000h, 0F0h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh
    db 0FEh
    db 'DIVIDE AND CONQUER'
    db 000h, 001h, 000h, 064h, 000h, 002h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 002h
    db 000h, 0C8h, 000h, 000h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 004h, 000h, 02Ch
    db 001h, 003h, 000h, 064h, 000h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db 'Ho w'
    db 000h, 000h
    db 'VoHx'
    db 000h, 000h, 064h, 06Fh, 0DCh, 078h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 006h, 000h
    db 0B3h, 03Ch, 030h, 076h, 000h, 000h, 0E8h, 003h, 032h, 000h, 0FFh, 0FFh, 0C0h, 000h, 040h, 001h
    db 0E0h, 000h, 030h, 001h, 010h, 001h, 0D0h, 000h, 001h, 000h, 000h, 000h, 000h, 000h, 080h, 000h
    db 0E0h, 000h, 010h, 000h, 030h, 000h, 050h, 000h, 002h, 000h, 000h, 000h, 090h, 000h, 040h, 001h
    db 030h, 000h, 010h, 001h, 0F0h, 000h, 0C0h, 000h, 003h, 000h, 000h, 000h, 000h, 000h, 040h, 000h
    db 020h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 004h, 000h, 000h, 000h, 090h, 000h, 010h, 001h
    db 090h, 000h, 0C0h, 000h, 0C0h, 000h, 0C0h, 000h, 005h, 000h, 000h, 000h, 010h, 001h, 040h, 001h
    db 070h, 000h, 020h, 001h, 020h, 001h, 020h, 001h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'FRUIT ALL THE TIME'
    db 000h, 003h, 000h, 064h, 000h, 002h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 000h
    db 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 001h, 000h, 02Ch
    db 001h, 003h, 000h, 064h, 000h, 000h, 000h, 064h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h
    db 077h, 000h, 000h, 012h, 070h, 020h, 077h, 000h, 000h
    db ' pHx'
    db 000h, 000h, 02Eh, 070h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 004h, 000h
    db 0B3h, 03Ch, 0A8h, 076h, 010h, 001h, 070h, 000h, 000h, 000h, 002h, 000h, 06Ch, 076h, 004h, 000h
    db 000h, 000h, 04Bh, 000h, 0FFh, 0FFh, 000h, 000h, 040h, 000h, 020h, 000h, 010h, 000h, 020h, 000h
    db 030h, 000h, 001h, 000h, 000h, 000h, 0E0h, 000h, 020h, 001h, 0D0h, 000h, 0F0h, 000h, 010h, 001h
    db 000h, 001h, 002h, 000h, 000h, 000h, 000h, 000h, 080h, 000h, 060h, 000h, 070h, 000h, 050h, 000h
    db 020h, 000h, 003h, 000h, 000h, 000h, 000h, 000h, 060h, 000h, 0F0h, 000h, 010h, 000h, 040h, 000h
    db 020h, 000h, 004h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 080h, 000h, 010h, 001h, 020h, 001h
    db 030h, 001h, 005h, 000h, 000h, 000h, 000h, 000h, 040h, 000h, 0B0h, 000h, 010h, 000h, 030h, 000h
    db 020h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'TRAFFIC PASSAGE'
    db 000h, 000h, 000h, 064h, 000h, 004h, 000h, 0C8h, 000h, 005h, 000h, 064h, 000h, 003h, 000h, 064h
    db 000h, 0FFh, 0FFh, 002h, 000h, 0C8h, 000h, 003h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 001h
    db 000h, 064h, 000h, 0FFh, 0FFh, 005h, 000h, 02Ch, 001h, 000h, 000h, 064h, 000h, 003h, 000h, 064h
    db 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h, 000h, 0E7h, 070h, 020h, 077h, 000h
    db 000h, 0F9h, 070h, 048h, 078h, 000h, 000h, 00Bh, 071h, 0DCh, 078h, 003h, 000h, 000h, 000h, 0FFh
    db 0FFh, 0E4h, 076h, 002h, 000h, 0B3h, 03Ch, 06Ch, 076h, 002h, 000h, 000h, 000h, 04Bh, 000h, 0FFh
    db 0FFh, 000h, 000h, 050h, 000h, 030h, 000h, 010h, 000h, 040h, 000h, 020h, 000h, 001h, 000h, 000h
    db 000h, 050h, 000h, 010h, 001h, 070h, 000h, 0F0h, 000h, 0C0h, 000h, 080h, 000h, 002h, 000h, 000h
    db 000h, 0B0h, 000h, 040h, 001h, 0F0h, 000h, 0C0h, 000h, 010h, 001h, 0E0h, 000h, 003h, 000h, 000h
    db 000h, 000h, 000h, 050h, 000h, 0C0h, 000h, 010h, 000h, 040h, 000h, 030h, 000h, 006h, 000h, 000h
    db 000h, 0E0h, 000h, 040h, 001h, 020h, 000h, 020h, 001h, 030h, 001h, 0F0h, 000h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'PASSING WALL'
    db 000h, 000h, 000h, 064h, 000h, 001h, 000h, 02Ch, 001h, 003h, 000h, 064h, 000h, 000h, 000h, 064h
    db 000h, 0FFh, 0FFh, 002h, 000h, 0C8h, 000h, 004h, 000h, 064h, 000h, 001h, 000h, 02Ch, 001h, 003h
    db 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h, 000h, 0A7h, 071h, 048h, 078h, 000h, 000h, 0B9h
    db 071h, 0DCh, 078h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 002h, 000h, 0B3h, 03Ch, 0FFh
    db 0FFh, 000h, 000h, 040h, 000h, 040h, 000h, 010h, 000h, 020h, 000h, 030h, 000h, 001h, 000h, 000h
    db 000h, 040h, 000h, 0A0h, 000h, 050h, 000h, 060h, 000h, 050h, 000h, 080h, 000h, 002h, 000h, 000h
    db 000h, 040h, 000h, 0B0h, 000h, 0B0h, 000h, 0A0h, 000h, 080h, 000h, 050h, 000h, 003h, 000h, 000h
    db 000h, 0E0h, 000h, 040h, 001h, 070h, 000h, 050h, 001h, 030h, 001h, 000h, 001h, 004h, 000h, 000h
    db 000h, 000h, 000h, 040h, 000h, 0C0h, 000h, 010h, 000h, 030h, 000h, 020h, 000h, 005h, 000h, 000h
    db 000h, 0E0h, 000h, 040h, 001h, 0F0h, 000h, 030h, 001h, 020h, 001h, 000h, 001h, 006h, 000h, 000h
    db 000h, 0FFh, 0FFh, 0FEh
    db 'SIX PACK'
    db 000h, 000h, 000h, 064h, 000h, 005h, 000h, 02Ch, 001h, 004h, 000h, 064h, 000h, 0FFh, 0FFh, 003h
    db 000h, 0C8h, 000h, 002h, 000h, 02Ch, 001h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 000h, 000h, 02Ch
    db 001h, 002h, 000h, 0C8h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 0B4h, 077h, 000h, 000h
    db 'Sr w'
    db 000h, 000h
    db 'arHx'
    db 000h, 000h, 06Fh, 072h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h
    db 0B3h, 03Ch, 030h, 076h, 000h, 000h, 058h, 002h, 03Ch, 000h, 0FFh, 0FFh, 000h, 000h, 0F0h, 000h
    db 0F0h, 000h, 010h, 000h, 040h, 000h, 0A0h, 000h, 001h, 000h, 000h, 000h, 0B0h, 000h, 040h, 001h
    db 090h, 000h, 030h, 001h, 010h, 001h, 0C0h, 000h, 002h, 000h, 000h, 000h, 000h, 000h, 080h, 000h
    db 050h, 000h, 040h, 000h, 010h, 000h, 060h, 000h, 003h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h
    db 030h, 000h, 030h, 001h, 010h, 001h, 0D0h, 000h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'DOUBLE TROUBLE'
    db 000h, 002h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 000h, 000h, 064h
    db 000h, 0FFh, 0FFh, 001h, 000h, 0C8h, 000h, 003h, 000h, 0C8h, 000h, 000h, 000h, 02Ch, 001h, 002h
    db 000h, 064h, 000h, 0FFh, 0FFh, 020h, 077h, 000h, 000h, 0F9h, 072h, 048h, 078h, 000h, 000h, 00Bh
    db 073h, 0DCh, 078h, 002h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 000h, 000h, 0B3h, 03Ch, 06Ch
    db 076h, 000h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 000h, 000h, 050h, 000h, 020h, 000h, 010h
    db 000h, 040h, 000h, 020h, 000h, 001h, 000h, 000h, 000h, 0E0h, 000h, 040h, 001h, 0D0h, 000h, 030h
    db 001h, 010h, 001h, 0F0h, 000h, 002h, 000h, 000h, 000h, 000h, 000h, 070h, 000h, 0F0h, 000h, 010h
    db 000h, 030h, 000h, 050h, 000h, 003h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 030h, 000h, 030h
    db 001h, 020h, 001h, 010h, 001h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'WHERE IS THE STONE?'
    db 000h, 001h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 0FFh, 0FFh, 003h
    db 000h, 0C8h, 000h, 002h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 002h, 000h, 02Ch
    db 001h, 000h, 000h, 064h, 000h, 001h, 000h, 064h, 000h, 0FFh, 0FFh, 048h, 078h, 000h, 000h, 098h
    db 073h, 020h, 077h, 000h, 000h, 0A6h, 073h, 048h, 078h, 000h, 000h, 0B4h, 073h, 0FFh, 0FFh, 0E4h
    db 076h, 002h, 000h, 0B3h, 03Ch, 0FFh, 0FFh, 0E0h, 000h, 040h, 001h, 0F0h, 000h, 030h, 001h, 020h
    db 001h, 000h, 001h, 001h, 000h, 000h, 000h, 010h, 000h, 070h, 000h, 040h, 000h, 030h, 000h, 020h
    db 000h, 050h, 000h, 002h, 000h, 000h, 000h, 0C0h, 000h, 040h, 001h, 030h, 000h, 020h, 001h, 000h
    db 001h, 0D0h, 000h, 003h, 000h, 000h, 000h, 000h, 000h, 0B0h, 000h, 0D0h, 000h, 020h, 000h, 040h
    db 000h, 080h, 000h, 004h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'AND WHERE'
    db 00Dh, 0FEh
    db 'IS THE TREE?'
    db 000h, 002h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 000h, 000h, 064h
    db 000h, 003h, 000h, 0C8h, 000h, 002h, 000h, 064h, 000h, 000h, 000h, 064h, 000h, 001h, 000h, 0C8h
    db 000h, 0FFh, 0FFh, 002h, 000h, 0C8h, 000h, 000h, 000h, 064h, 000h, 001h, 000h, 064h, 000h, 003h
    db 000h, 064h, 000h, 0FFh, 0FFh, 001h, 000h, 02Ch, 001h, 000h, 000h, 064h, 000h, 003h, 000h, 064h
    db 000h, 0FFh, 0FFh, 048h, 078h, 000h, 000h
    db '9t w'
    db 000h, 000h, 05Bh, 074h, 0B4h, 077h, 000h, 000h, 06Dh, 074h, 0DCh, 078h, 003h, 000h, 000h, 000h
    db 0FFh, 0FFh, 06Ch, 076h, 003h, 000h, 000h, 000h, 04Bh, 000h, 0FFh, 0FFh, 000h, 000h, 030h, 000h
    db 0A0h, 000h, 0F0h, 0FFh, 010h, 000h, 020h, 000h, 001h, 000h, 000h, 000h, 030h, 000h, 0A0h, 000h
    db 040h, 000h, 060h, 000h, 050h, 000h, 080h, 000h, 002h, 000h, 000h, 000h, 0A0h, 000h, 0F0h, 000h
    db 080h, 000h, 0B0h, 000h, 0C0h, 000h, 0E0h, 000h, 003h, 000h, 000h, 000h, 000h, 000h, 070h, 000h
    db 0E0h, 000h, 010h, 000h, 030h, 000h, 060h, 000h, 004h, 000h, 000h, 000h, 0E0h, 000h, 030h, 001h
    db 0C0h, 000h, 0F0h, 000h, 000h, 001h, 010h, 001h, 005h, 000h, 000h, 000h, 0D0h, 000h, 030h, 001h
    db 020h, 000h, 010h, 001h, 020h, 001h, 0E0h, 000h, 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'NEARLY DROWNING'
    db 000h, 002h, 000h, 064h, 000h, 003h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 005h, 000h, 064h
    db 000h, 0FFh, 0FFh, 004h, 000h, 0C8h, 000h, 000h, 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 005h
    db 000h, 064h, 000h, 0FFh, 0FFh, 005h, 000h, 02Ch, 001h, 004h, 000h, 064h, 000h, 000h, 000h, 064h
    db 000h, 0FFh, 0FFh, 020h, 077h, 000h, 000h, 012h, 075h, 020h, 077h, 000h, 000h
    db '$uHx'
    db 000h, 000h, 036h, 075h, 0DCh, 078h, 005h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h
    db 0B3h, 03Ch, 0FFh, 0FFh, 000h, 000h, 040h, 000h, 050h, 000h, 020h, 000h, 010h, 000h, 030h, 000h
    db 001h, 000h, 000h, 000h, 090h, 000h, 0F0h, 000h, 040h, 000h, 0B0h, 000h, 0C0h, 000h, 0E0h, 000h
    db 002h, 000h, 000h, 000h, 0C0h, 000h, 000h, 001h, 080h, 000h, 0D0h, 000h, 0E0h, 000h, 0F0h, 000h
    db 003h, 000h, 000h, 000h, 000h, 000h, 090h, 000h, 0E0h, 000h, 010h, 000h, 030h, 000h, 070h, 000h
    db 004h, 000h, 000h, 000h, 000h, 001h, 040h, 001h, 0B0h, 000h, 050h, 001h, 030h, 001h, 010h, 001h
    db 005h, 000h, 000h, 000h, 0F0h, 000h, 030h, 001h, 020h, 000h, 010h, 001h, 020h, 001h, 000h, 001h
    db 006h, 000h, 000h, 000h, 0FFh, 0FFh, 0FEh
    db 'STILL DROWNING'
    db 000h, 001h, 000h, 064h, 000h, 000h, 000h, 0C8h, 000h, 0FFh, 0FFh, 004h, 000h, 0C8h, 000h, 005h
    db 000h, 0C8h, 000h, 001h, 000h, 064h, 000h, 003h, 000h, 064h, 000h, 0FFh, 0FFh, 002h, 000h, 02Ch
    db 001h, 005h, 000h, 064h, 000h, 004h, 000h, 064h, 000h, 000h, 000h, 064h, 000h, 0FFh, 0FFh, 020h
    db 077h, 000h, 000h, 0D8h, 075h, 020h, 077h, 000h, 000h, 0E2h, 075h, 048h, 078h, 000h, 000h, 0F4h
    db 075h, 0DCh, 078h, 000h, 000h, 000h, 000h, 0FFh, 0FFh, 0E4h, 076h, 003h, 000h, 0B3h, 03Ch, 06Ch
    db 076h, 003h, 000h, 000h, 000h, 04Bh, 000h, 0FFh, 0FFh, 010h, 000h, 00Bh, 000h, 008h, 000h, 008h
    db 000h, 079h, 023h, 09Fh, 023h, 0B0h, 023h, 0D9h, 023h, 0EAh, 023h, 093h, 024h
    db 8 dup (000h)
    db '+%^%'
    db 00Eh, 01Ch, 000h, 00Dh, 01Ah, 00Dh, 000h, 00Dh, 01Ah, 00Dh
    db 12 dup (000h)
    db 034h, 00Dh, 038h, 00Dh, 0C4h, 009h, 010h, 000h, 016h, 000h, 008h, 000h, 008h, 000h, 0B1h, 025h
    db 0C9h, 025h, 067h, 026h, 081h, 026h, 02Eh, 027h, 048h, 027h
    db '0(D('
    db 08Fh, 028h, 0A3h, 028h, 0EEh, 028h, 014h, 029h, 00Eh, 01Ch, 03Ch, 00Dh, 04Ah, 00Dh, 058h, 00Dh
    db 066h, 00Dh, 074h, 00Dh, 082h, 00Dh, 090h, 00Dh, 09Eh, 00Dh, 0ACh, 00Dh, 0BAh, 00Dh, 0C8h, 00Dh
    db 0D6h, 00Dh, 078h, 005h, 010h, 000h, 016h, 000h, 008h, 000h, 008h, 000h, 00Eh, 01Ch, 00Eh, 01Ch
    db 00Eh, 01Ch, 00Eh, 01Ch
    db '[)s)'
    db 8 dup (000h)
    db 'S*v*'
    db 00Eh, 01Ch, 0E4h, 00Dh, 0E4h, 00Dh, 0E4h, 00Dh, 0E4h, 00Dh
    db 12 dup (000h)
    db 0FAh, 00Dh, 000h, 000h, 020h, 003h, 010h, 000h, 018h, 000h, 008h, 000h, 008h, 000h, 087h, 02Ah
    db 0B5h, 02Ah
    db 16 dup (000h)
    db 00Ch
    db '+X+~+'
    db 0FEh, 00Dh
    db 18 dup (000h)
    db 01Ch, 00Eh, 000h, 000h, 000h, 000h, 008h, 000h, 00Ah, 000h, 004h, 000h, 004h, 000h, 09Ch, 014h
    db 009h, 015h, 03Bh, 015h, 082h, 015h, 0B4h, 015h, 0D7h, 015h, 0F6h, 016h, 02Ah, 017h, 0E6h, 017h
    db 00Ah, 018h, 0C8h, 018h, 0E6h, 018h, 0FBh, 019h, 042h, 01Ah, 07Eh, 01Ah, 029h, 01Bh, 0BEh, 01Bh
    db 0D6h, 01Bh, 00Eh, 01Ch, 020h, 00Eh, 02Ah, 00Eh, 032h, 00Eh, 046h, 00Eh, 05Ah, 00Eh, 06Eh, 00Eh
    db 001h, 000h, 000h, 000h, 007h, 000h, 04Ch, 004h, 02Ch, 001h, 000h, 000h, 001h, 000h, 06Ah, 077h
    db 008h, 000h, 003h, 000h, 004h, 000h, 004h, 000h, 0A8h, 01Dh, 0D5h, 01Dh, 09Ch, 01Eh, 0C0h, 01Eh
    db 024h, 01Fh, 043h, 01Fh, 0F6h, 016h, 0E2h, 01Fh, 0E6h, 017h, 068h, 020h, 0C8h, 018h, 0C1h, 020h
    db 0E0h, 019h, 00Eh, 01Ch, 095h, 021h, 095h, 021h, 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch, 082h, 00Eh
    db 082h, 00Eh, 088h, 00Eh, 09Ch, 00Eh, 05Ah, 00Eh, 06Eh, 00Eh, 001h, 000h, 000h, 000h, 007h, 000h
    db 02Ch, 001h, 02Ch, 001h, 0BCh, 002h, 001h, 000h, 020h, 077h, 006h, 000h, 00Ah, 000h, 004h, 000h
    db 004h, 000h, 09Ch, 014h, 009h, 015h, 03Bh, 015h, 082h, 015h, 0B4h, 015h, 0D7h, 015h, 0F6h, 016h
    db 02Ah, 017h, 0E6h, 017h, 00Ah, 018h, 0C8h, 018h, 0E6h, 018h, 0FBh, 019h, 042h, 01Ah, 07Eh, 01Ah
    db 029h, 01Bh, 0BEh, 01Bh, 0D6h, 01Bh, 00Eh, 01Ch, 0B0h, 00Eh, 0BAh, 00Eh, 0C2h, 00Eh, 0D6h, 00Eh
    db 0EAh, 00Eh, 0FEh, 00Eh, 001h, 000h, 000h, 000h, 007h, 000h, 028h, 00Ah, 0F4h, 001h, 000h, 000h
    db 003h, 000h, 0FEh, 077h, 006h, 000h, 005h, 000h, 004h, 000h, 004h, 000h, 0A8h, 01Dh, 0D5h, 01Dh
    db 09Ch, 01Eh, 0C0h, 01Eh, 024h, 01Fh, 043h, 01Fh, 0F6h, 016h, 0E2h, 01Fh, 0E6h, 017h, 068h, 020h
    db 0C8h, 018h, 0C1h, 020h, 0E0h, 019h, 00Eh, 01Ch, 095h, 021h, 095h, 021h, 00Eh, 01Ch, 00Eh, 01Ch
    db 00Eh, 01Ch, 012h, 00Fh, 012h, 00Fh, 012h, 00Fh, 012h, 00Fh, 0EAh, 00Eh, 0FEh, 00Eh, 001h, 000h
    db 000h, 000h, 007h, 000h, 0F4h, 001h, 0F4h, 001h, 08Ch, 000h, 003h, 000h, 0B4h, 077h, 006h, 000h
    db 00Eh, 000h, 003h, 000h, 004h, 000h, 09Ch, 014h, 009h, 015h, 03Bh, 015h, 082h, 015h, 0B4h, 015h
    db 0D7h, 015h, 0F6h, 016h, 02Ah, 017h, 0E6h, 017h, 00Ah, 018h, 0C8h, 018h, 0E6h, 018h, 0FBh, 019h
    db 042h, 01Ah, 07Eh, 01Ah, 029h, 01Bh, 0BEh, 01Bh, 0D6h, 01Bh, 00Eh, 01Ch, 01Ch, 00Fh, 01Ch, 00Fh
    db 096h, 00Fh, 0AAh, 00Fh, 0BEh, 00Fh, 0D2h, 00Fh, 001h, 000h, 000h, 000h, 007h, 000h, 040h, 006h
    db 090h, 001h, 000h, 000h, 002h, 000h, 092h, 078h, 008h, 000h, 003h, 000h, 003h, 000h, 004h, 000h
    db 0A8h, 01Dh, 0D5h, 01Dh, 09Ch, 01Eh, 0C0h, 01Eh, 024h, 01Fh, 043h, 01Fh, 0F6h, 016h, 0E2h, 01Fh
    db 0E6h, 017h, 068h, 020h, 0C8h, 018h, 0C1h, 020h, 0E0h, 019h, 00Eh, 01Ch, 095h, 021h, 095h, 021h
    db 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch, 0E6h, 00Fh, 0EEh, 00Fh, 0F6h, 00Fh, 00Ah, 010h, 0BEh, 00Fh
    db 0D2h, 00Fh, 001h, 000h, 000h, 000h, 007h, 000h, 090h, 001h, 090h, 001h, 078h, 005h, 002h, 000h
    db 048h, 078h, 008h, 000h, 00Bh, 000h, 003h, 000h, 002h, 000h, 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch
    db 00Eh, 01Ch, 00Fh, 01Ch, 027h, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch
    db 00Eh, 01Ch, 048h, 01Ch, 06Bh, 01Ch, 081h, 01Ch, 0EEh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch
    db 01Eh, 010h, 01Eh, 010h, 01Eh, 010h, 01Eh, 010h, 01Eh, 010h, 01Eh, 010h, 002h, 000h, 002h
    db 9 dup (000h)
    db 004h, 000h, 026h, 079h, 008h, 000h, 00Bh, 000h, 003h, 000h, 002h, 000h, 00Eh, 01Ch, 00Eh, 01Ch
    db 00Eh, 01Ch, 00Eh, 01Ch, 00Fh, 01Ch, 027h, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch
    db 00Eh, 01Ch, 00Eh, 01Ch, 048h, 01Ch, 06Bh, 01Ch, 081h, 01Ch, 0EEh, 01Ch, 00Eh, 01Ch, 00Eh, 01Ch
    db 00Eh, 01Ch, 01Eh, 010h, 01Eh, 010h, 01Eh, 010h, 01Eh, 010h, 01Eh, 010h, 01Eh, 010h, 002h, 000h
    db 002h
    db 9 dup (000h)
    db 004h, 000h, 0DCh, 078h, 008h, 000h, 010h, 000h, 096h, 02Bh, 0E4h, 02Bh, 097h, 02Ch, 0A9h, 02Ch
    db 00Eh, 000h, 0B8h, 00Bh, 01Dh, 001h, 000h, 000h, 008h, 000h, 010h, 000h, 096h, 02Bh, 0E4h, 02Bh
    db 097h, 02Ch, 0A9h, 02Ch, 015h, 000h, 058h, 01Bh, 01Eh, 001h, 000h, 000h, 008h, 000h, 010h, 000h
    db 096h, 02Bh, 0E4h, 02Bh, 097h, 02Ch, 0A9h, 02Ch, 01Ch, 000h, 088h, 013h, 01Fh, 001h, 000h, 000h
    db 008h, 000h, 010h, 000h, 096h, 02Bh, 0E4h, 02Bh, 097h, 02Ch, 0A9h, 02Ch, 023h, 000h, 088h, 013h
    db 020h, 001h, 000h, 000h, 008h, 000h, 010h, 000h, 096h, 02Bh, 0E4h, 02Bh, 097h, 02Ch, 0A9h, 02Ch
    db 02Ah, 000h, 040h, 01Fh, 021h, 001h, 000h, 000h, 008h, 000h, 010h, 000h, 096h, 02Bh, 0E4h, 02Bh
    db 097h, 02Ch, 0A9h, 02Ch, 032h, 000h, 058h, 01Bh, 022h, 001h, 000h, 000h, 008h, 000h, 010h, 000h
    db 096h, 02Bh, 0E4h, 02Bh, 097h, 02Ch, 0A9h, 02Ch, 039h, 000h, 0B8h, 00Bh, 023h, 001h, 000h, 000h
    db 008h, 000h, 010h, 000h, 096h, 02Bh, 0E4h, 02Bh, 097h, 02Ch, 0A9h, 02Ch, 040h, 000h, 088h, 013h
    db 024h, 001h, 000h, 000h, 008h, 000h, 010h, 000h, 096h, 02Bh, 0E4h, 02Bh, 097h, 02Ch, 0A9h, 02Ch
    db 047h, 000h, 010h, 027h, 025h, 001h, 000h, 000h, 008h, 000h, 010h, 000h, 096h, 02Bh, 0E4h, 02Bh
    db 097h, 02Ch, 0A9h, 02Ch, 039h, 000h, 001h, 000h, 028h, 001h, 001h, 000h, 008h, 000h, 010h, 000h
    db 096h, 02Bh, 0E4h, 02Bh, 097h, 02Ch, 0A9h, 02Ch, 039h, 000h, 000h, 000h, 029h, 001h, 002h
    db 305 dup (000h)
_DATA ends
DGROUP group _DATA
extrn ext_0A67:far
extrn ext_1A38:far
extrn ext_2BC6:far
end
