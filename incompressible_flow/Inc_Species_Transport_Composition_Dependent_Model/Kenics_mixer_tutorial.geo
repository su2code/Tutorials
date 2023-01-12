// Gmsh project created on Mon Mar 28 17:05:52 2022
//-----------------------------------------------------------------------------------//
// Cristopher Morales Ubal, TU Eindhoven, 06.01.2023, 3D Kenics static mixer
//-----------------------------------------------------------------------------------//
//
//
//----------------------------------------------------------------------------------//
// Defining geometry parameters
//----------------------------------------------------------------------------------//
//
//Diameter
D=20/1000;  
//Blade thickness
a=D/10;
//ENTRANCE and EXIT LENGTH
LE=4*D;  
// Aspect ratio
AR= 1;  
//length of element
L=AR*D;
//+
//Radius
R=D/2;
//create a square at the center of the kenics mixer for creating a structured mesh
b=D/4;
// Defining twisting angle
DefineConstant[ angle={180,Min 0, Max 360,Step 1, Name "Parameter/twisting angle"}];
//+
angle=180;
//
//----------------------------------------------------------------------------------//
// Defining mesh parameters
//----------------------------------------------------------------------------------//
//
// n element cross section
nc= 10;
// n element axial length
nx= 10; 
// Progression
PR= 1;
// F: Factor refining mesh inside blades
F= 1;
// FE: Factor refining mesh entrance and exit length
FE = 3;
//
//----------------------------------------------------------------------------------//
// Defining points for creating circle, blade and blocks for structured mesh
//----------------------------------------------------------------------------------//
//
Point(2) = {0, 0, LE, 1.0};
//+
Point(3)={Sqrt((R*R)-(a*a/4)),a/2,LE,1};
//+
Point(4)={-Sqrt((R*R)-(a*a/4)),a/2,LE,1};
//+
Point(5)={Sqrt((R*R)-(a*a/4)),-a/2,LE,1};
//+
Point(6)={-Sqrt((R*R)-(a*a/4)),-a/2,LE,1};
//+
Point(7) = {0, R, LE, 1.0};
//+
Point(8) = {0, -R, LE, 1.0};
//+
Point(9) = {-R, 0, LE, 1.0};
//+
Point(10) = {R, 0, LE, 1.0};
//
Point(11)={R*Cos(Pi/4),R*Sin(Pi/4),LE,1};
//+
Point(12)={-R*Cos(Pi/4),R*Sin(Pi/4),LE,1};
//+
Point(13)={R*Cos(Pi/4),-R*Sin(Pi/4),LE,1};
//+
Point(14)={-R*Cos(Pi/4),-R*Sin(Pi/4),LE,1};
//
Point(15)={b,b,LE,1};
//+
Point(16)={b,-b,LE,1};
//+
Point(17)={-b,b,LE,1};
//+
Point(18)={-b,-b,LE,1};
//+
Point(19)={b,a/2,LE,1};
//+
Point(20)={-b,a/2,LE,1};
//+
Point(21)={b,-a/2,LE,1};
//+
Point(22)={-b,-a/2,LE,1};
//+
Point(23)={a/2,a/2,LE,1};
//+
Point(24)={a/2,-a/2,LE,1};
//+
Point(25)={-a/2,a/2,LE,1};
//+
Point(26)={-a/2,-a/2,LE,1};
//+
Point(27)={a/2,Sqrt((R*R)-(a*a/4)),LE,1};
//+
Point(28)={a/2,-Sqrt((R*R)-(a*a/4)),LE,1};
//+
Point(29)={-a/2,Sqrt((R*R)-(a*a/4)),LE,1};
//+
Point(30)={-a/2,-Sqrt((R*R)-(a*a/4)),LE,1};
//+
Point(31)={a/2,b,LE,1};
//+
Point(32)={a/2,-b,LE,1};
//+
Point(33)={-a/2,b,LE,1};
//+
Point(34)={-a/2,-b,LE,1};
//----------------------------------------------------------------------------------//
// Creating line and circles
//----------------------------------------------------------------------------------//
//
Line(37) = {11, 15};
//+
Line(38) = {15, 19};
//+
Line(39) = {17, 20};
//+
Line(40) = {12, 17};
//+
Line(41) = {15, 31};
//+
Line(42) = {16, 21};
//+
Line(43) = {22, 18};
//+
Line(44) = {16, 32};
//+
Line(45) = {13, 16};
//+
Line(46) = {14, 18};
//+
Circle(47) = {3, 2, 11};
//+
Circle(48) = {11, 2, 27};
//+
Circle(49) = {27,2,29};
//+
Circle(50) = {29,2,12};
//+
Circle(51) = {12, 2, 4};
//+
Circle(52) = {6, 2, 14};
//+
Circle(54) = {13, 2, 28};
//+
Circle(55) = {28, 2, 30};
//+
Circle(56) = {30, 2, 14};
//+
Circle(57) = {13, 2, 5};
//+
Line(58) = {3, 19};
//+
Line(59) = {19, 23};
//+
Line(60) = {20, 4};
//+
Line(61) = {5, 21};
//+
Line(62) = {21, 24};
//+
Line(63) = {22, 6};
//+
Line(64)={23,25};
//+
Line(65)={25,20};
//+
Line(66)={24,26};
//+
Line(67)={26,22};
//+
Line(68) = {27, 31};
//+
Line(69) = {31, 23};
//+
Line(70) = {29, 33};
//+
Line(71) = {33, 25};
//+
Line(72) = {24, 32};
//+
Line(73) = {32, 28};
//+
Line(74) = {26, 34};
//+
Line(75) = {34, 30};
//+
Line(76) = {31, 33};
//+
Line(77) = {33, 17};
//+
Line(78) = {32, 34};
//+
Line(79) = {34, 18};
//+
//----------------------------------------------------------------------------------//
// Defining curve loops and plane surfaces
//----------------------------------------------------------------------------------//
//
Curve Loop(1) = {47, 37, 38, -58};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {48, 68, -41, -37};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {38, 59, -69, -41};
//+
Plane Surface(3) = {3};
//+
Curve Loop(4) = {69, 64, -71, -76};
//+
Plane Surface(4) = {4};
//+
Curve Loop(5) = {68, 76, -70, -49};
//+
Plane Surface(5) = {5};
//+
Curve Loop(6) = {70, 77, -40, -50};
//+
Plane Surface(6) = {6};
//+
Curve Loop(7) = {71, 65, -39, -77};
//+
Plane Surface(7) = {7};
//+
Curve Loop(8) = {39, 60, -51, 40};
//+
Plane Surface(8) = {8};
//+
Curve Loop(9) = {57, 61, -42, -45};
//+
Plane Surface(9) = {9};
//+
Curve Loop(10) = {42, 62, 72, -44};
//+
Plane Surface(10) = {10};
//+
Curve Loop(11) = {72, 78, -74, -66};
//+
Plane Surface(11) = {11};
//+
Curve Loop(12) = {74, 79, -43, -67};
//+
Plane Surface(12) = {12};
//+
Curve Loop(13) = {43, -46, -52, -63};
//+
Plane Surface(13) = {13};
//+
Curve Loop(14) = {45, 44, 73, -54};
//+
Plane Surface(14) = {14};
//+
Curve Loop(15) = {73, 55, -75, -78};
//+
Plane Surface(15) = {15};
//+
Curve Loop(16) = {75, 56, 46, -79};
//+
Plane Surface(16) = {16};
//+
//----------------------------------------------------------------------------------//
// make structured mesh with transfinite curves and transfinite surfaces
//----------------------------------------------------------------------------------//
//
Transfinite Curve {47, 37, 38, 58} = nc Using Progression PR;
//+
Transfinite Curve {37, 48, 68, 41} = nc Using Progression PR;
//+
Transfinite Curve {68, 49, 70, 76} = nc Using Progression PR;
//+
Transfinite Curve {70, 50, 40, 77} = nc Using Progression PR;
//+
Transfinite Curve {38, 41, 69, 59} = nc Using Progression PR;
//+
Transfinite Curve {69, 76, 71, 64} = nc Using Progression PR;
//+
Transfinite Curve {71, 77, 39, 65} = nc Using Progression PR;
//+
Transfinite Curve {39, 40, 51, 60} = nc Using Progression PR;
//+
Transfinite Curve {57, 61, 42, 45} = nc Using Progression PR;
//+
Transfinite Curve {42, 62, 72, 44} = nc Using Progression PR;
//+
Transfinite Curve {72, 66, 74, 78} = nc Using Progression PR;
//+
Transfinite Curve {74, 67, 43, 79} = nc Using Progression PR;
//+
Transfinite Curve {43, 63, 52, 46} = nc Using Progression PR;
//+
Transfinite Curve {45, 44, 73, 54} = nc Using Progression PR;
//+
Transfinite Curve {73, 78, 75, 55} = nc Using Progression PR;
//+
Transfinite Curve {75, 79, 46, 56} = nc Using Progression PR;
//+
Transfinite Surface {1};
//+
Transfinite Surface {2};
//+
Transfinite Surface {5};
//+
Transfinite Surface {6};
//+
Transfinite Surface {8};
//+
Transfinite Surface {7};
//+
Transfinite Surface {4};
//+
Transfinite Surface {3};
//+
Transfinite Surface {9};
//+
Transfinite Surface {10};
//+
Transfinite Surface {11};
//+
Transfinite Surface {12};
//+
Transfinite Surface {13};
//+
Transfinite Surface {16};
//+
Transfinite Surface {15};
//+
Transfinite Surface {14};
//+
Recombine Surface "*";
//+
//----------------------------------------------------------------------------------//
// Create First blade
//----------------------------------------------------------------------------------//
//
out1[]=Extrude{{0,0,L},{0,0,1},{0,0,0.25},angle*Pi/180}{Surface{1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16};Layers{F*nx};Recombine;};
//+
//----------------------------------------------------------------------------------//
// Translate first face of the inlet and rotate 180 degrees for creating the second blade
//----------------------------------------------------------------------------------//
//
S115[]=Translate {0, 0, 2*L} {Duplicata {Surface{1};  Surface{2}; Surface{3}; Surface{4}; Surface{5}; Surface{6}; Surface{7}; Surface{8};Surface{9};Surface{10};Surface{11};Surface{12};Surface{13};Surface{14};Surface{15};Surface{16};}};
//+
S116[] = Rotate{ {0,0,1},{0,0,0.25},Pi/2} {Surface{S115[]};};
//+
Recombine Surface "*";
//+
//----------------------------------------------------------------------------------//
// make structured mesh with transfinite curves and surfaces
//----------------------------------------------------------------------------------//
//
Transfinite Curve {473, 474, 475, 476} = nc Using Progression PR;
//+
Transfinite Curve {501, 476, 481, 500} = nc Using Progression PR;
//+
Transfinite Curve {475, 479, 480, 481} = nc Using Progression PR;
//+
Transfinite Curve {504, 500, 484, 505} = nc Using Progression PR;
//+
Transfinite Curve {509, 505, 489, 494} = nc Using Progression PR;
//+
Transfinite Curve {489, 485, 491, 490} = nc Using Progression PR;
//+
Transfinite Curve {494, 490, 496, 495} = nc Using Progression PR;
//+
Transfinite Curve {484, 480, 486, 485} = nc Using Progression PR;
//+
Transfinite Curve {436, 433, 434, 435} = nc Using Progression PR;
//+
Transfinite Curve {444, 435, 440, 445} = nc Using Progression PR;
//+
Transfinite Curve {440, 434, 438, 439} = nc Using Progression PR;
//+
Transfinite Curve {449, 445, 451, 450} = nc Using Progression PR;
//+
Transfinite Curve {451, 439, 456, 455} = nc Using Progression PR;
//+
Transfinite Curve {464, 450, 459, 465} = nc Using Progression PR;
//+
Transfinite Curve {459, 455, 461, 460} = nc Using Progression PR;
//+
Transfinite Curve {469, 465, 460, 470} = nc Using Progression PR;
//+
Transfinite Surface {432};
//+
Transfinite Surface {437};
//+
Transfinite Surface {442};
//+
Transfinite Surface {447};
//+
Transfinite Surface {452};
//+
Transfinite Surface {462};
//+
Transfinite Surface {457};
//+
Transfinite Surface {467};
//+
Transfinite Surface {472};
//+
Transfinite Surface {497};
//+
Transfinite Surface {477};
//+
Transfinite Surface {502};
//+
Transfinite Surface {507};
//+
Transfinite Surface {482};
//+
Transfinite Surface {487};
//+
Transfinite Surface {492};
//+
Recombine Surface "*";
//+
//----------------------------------------------------------------------------------//
// Create Second blade
//----------------------------------------------------------------------------------//
//
out2[]=Extrude{{0,0,-L},{0,0,1},{0,0,0.25},-angle*Pi/180}{Surface{432,437,442,447,452,462,457,467,472,497,477,502,507,482,487,492};Layers{F*nx};Recombine;};
//+
//----------------------------------------------------------------------------------//
// repeat the process above for creating the third blade
//----------------------------------------------------------------------------------//
//
S117[]=Translate {0, 0, 3*L} {Duplicata {Surface{1};  Surface{2}; Surface{3}; Surface{4}; Surface{5}; Surface{6}; Surface{7}; Surface{8};Surface{9};Surface{10};Surface{11};Surface{12};Surface{13};Surface{14};Surface{15};Surface{16};}};
//+
// third is rotate 180 degrees with respect to the first blade( in other words, they are parallell)
//
S118[] = Rotate{ {0,0,1},{0,0,0.25},Pi} {Surface{S117[]};};
//+
Recombine Surface "*";
//+
Transfinite Curve {897, 896, 892, 898} = nc Using Progression PR;
//+
Transfinite Curve {911, 907, 891, 896} = nc Using Progression PR;
//+
Transfinite Curve {907, 906, 902, 886} = nc Using Progression PR;
//+
Transfinite Curve {902, 903, 878, 883} = nc Using Progression PR;
//+
Transfinite Curve {892, 891, 887, 893} = nc Using Progression PR;
//+
Transfinite Curve {887, 886, 882, 888} = nc Using Progression PR;
//+
Transfinite Curve {882, 883, 877, 881} = nc Using Progression PR;
//+
Transfinite Curve {877, 878, 875, 876} = nc Using Progression PR;
//+
Transfinite Curve {872, 871, 867, 862} = nc Using Progression PR;
//+
Transfinite Curve {867, 866, 852, 861} = nc Using Progression PR;
//+
Transfinite Curve {852, 851, 847, 853} = nc Using Progression PR;
//+
Transfinite Curve {847, 846, 837, 842} = nc Using Progression PR;
//+
Transfinite Curve {837, 838, 835, 836} = nc Using Progression PR;
//+
Transfinite Curve {862, 861, 857, 863} = nc Using Progression PR;
//+
Transfinite Curve {857, 853, 841, 858} = nc Using Progression PR;
//+
Transfinite Curve {841, 842, 836, 840} = nc Using Progression PR;
//+
Transfinite Surface {894};
//+
Transfinite Surface {909};
//+
Transfinite Surface {889};
//+
Transfinite Surface {884};
//+
Transfinite Surface {904};
//+
Transfinite Surface {899};
//+
Transfinite Surface {879};
//+
Transfinite Surface {874};
//+
Transfinite Surface {869};
//+
Transfinite Surface {864};
//+
Transfinite Surface {849};
//+
Transfinite Surface {844};
//+
Transfinite Surface {834};
//+
Transfinite Surface {839};
//+
Transfinite Surface {854};
//+
Transfinite Surface {859};
//+
Recombine Surface "*";
//
//----------------------------------------------------------------------------------//
// Create Third blade
//----------------------------------------------------------------------------------//
//
out3[]=Extrude{{0,0,-L},{0,0,1},{0,0,0.25},-angle*Pi/180}{Surface{894,909,889,884,904,899,879,874,869,864,849,844,834,839,854,859};Layers{F*nx};Recombine;};
//
//----------------------------------------------------------------------------------//
// Create exit pipe (mainly repeating the same procedure above but without twisting, angle=0)
//----------------------------------------------------------------------------------//
//
// note that the exit lenght is 1.5*LE=6D in order to reduce the effect of the outlet BC 
S119[]=Translate {0, 0, 3*L+1.5*LE} {Duplicata {Surface{1};  Surface{2}; Surface{3}; Surface{4}; Surface{5}; Surface{6}; Surface{7}; Surface{8};Surface{9};Surface{10};Surface{11};Surface{12};Surface{13};Surface{14};Surface{15};Surface{16};}};
//+
Line(1306) = {2722, 2851};
//+
Line(1307) = {2751, 2867};
//+
Line(1308) = {2767, 2887};
//+
Line(1309) = {2817, 2903};
//+
Circle(1310) = {2833, 2713, 2920};
//+
Circle(1311) = {2712, 2713, 2847};
//+
Curve Loop(17) = {1232, 1311, 1270, -1306};
//+
Plane Surface(1304) = {17};
//+
Curve Loop(18) = {1240, 1307, -1275, -1306};
//+
Plane Surface(1305) = {18};
//+
Curve Loop(19) = {1245, 1308, 1282, -1307};
//+
Plane Surface(1306) = {19};
//+
Curve Loop(20) = {1260, 1309, 1287, -1308};
//+
Plane Surface(1307) = {20};
//+
Curve Loop(21) = {1265, 1310, 1292, -1309};
//+
Plane Surface(1308) = {21};
//+
Transfinite Curve {1266, 1256, 1261, 1265} = nc Using Progression PR;
//+
Transfinite Curve {1257, 1251, 1255, 1256} = nc Using Progression PR;
//+
Transfinite Curve {1251, 1252, 1235, 1247} = nc Using Progression PR;
//+
Transfinite Curve {1235, 1234, 1230, 1236} = nc Using Progression PR;
//+
Transfinite Curve {1255, 1246, 1260, 1261} = nc Using Progression PR;
//+
Transfinite Curve {1246, 1247, 1241, 1245} = nc Using Progression PR;
//+
Transfinite Curve {1236, 1231, 1240, 1241} = nc Using Progression PR;
//+
Transfinite Curve {1231, 1230, 1229, 1232} = nc Using Progression PR;
//+
Transfinite Curve {1265, 1309, 1292, 1310} = nc Using Progression PR;
//+
Transfinite Curve {1309, 1260, 1308, 1287} = nc Using Progression PR;
//+
Transfinite Curve {1308, 1245, 1307, 1282} = nc Using Progression PR;
//+
Transfinite Curve {1307, 1240, 1306, 1275} = nc Using Progression PR;
//+
Transfinite Curve {1306, 1232, 1311, 1270} = nc Using Progression PR;
//+
Transfinite Curve {1292, 1286, 1290, 1291} = nc Using Progression PR;
//+
Transfinite Curve {1286, 1287, 1281, 1285} = nc Using Progression PR;
//+
Transfinite Curve {1281, 1282, 1276, 1280} = nc Using Progression PR;
//+
Transfinite Curve {1276, 1275, 1271, 1277} = nc Using Progression PR;
//+
Transfinite Curve {1271, 1270, 1269, 1272} = nc Using Progression PR;
//+
Transfinite Curve {1290, 1285, 1301, 1305} = nc Using Progression PR;
//+
Transfinite Curve {1301, 1280, 1296, 1300} = nc Using Progression PR;
//+
Transfinite Curve {1296, 1277, 1272, 1297} = nc Using Progression PR;
//+
Transfinite Surface {1253};
//+
Transfinite Surface {1248};
//+
Transfinite Surface {1233};
//+
Transfinite Surface {1263};
//+
Transfinite Surface {1258};
//+
Transfinite Surface {1243};
//+
Transfinite Surface {1238};
//+
Transfinite Surface {1228};
//+
Transfinite Surface {1308};
//+
Transfinite Surface {1307};
//+
Transfinite Surface {1306};
//+
Transfinite Surface {1305};
//+
Transfinite Surface {1304};
//+
Transfinite Surface {1288};
//+
Transfinite Surface {1283};
//+
Transfinite Surface {1278};
//+
Transfinite Surface {1273};
//+
Transfinite Surface {1268};
//+
Transfinite Surface {1303};
//+
Transfinite Surface {1298};
//+
Transfinite Surface {1293};
//+
Recombine Surface "*";
//+
out4[]=Extrude{{0,0,-1.5*LE},{0,0,1},{0,0,0.25},0}{Surface{1253,1248,1233,1263,1258,1243,1238,1228,1308,1307,1306,1305,1304,1288,1283,1278,1273,1268,1303,1298,1293};Layers{{2*FE*nx/3,FE*nx/3},{0.75,1}};Recombine;};
//+
//----------------------------------------------------------------------------------//
// Create entrance pipe (similar to the procedure above)
//----------------------------------------------------------------------------------//
//
S120[]=Translate {0, 0, -LE} {Duplicata {Surface{1};  Surface{2}; Surface{3}; Surface{4}; Surface{5}; Surface{6}; Surface{7}; Surface{8};Surface{9};Surface{10};Surface{11};Surface{12};Surface{13};Surface{14};Surface{15};Surface{16};}};
//+
Transfinite Curve {1732, 1722, 1727, 1731} = nc Using Progression PR;
//+
Transfinite Curve {1722, 1723, 1717, 1721} = nc Using Progression PR;
//+
Transfinite Curve {1717, 1718, 1701, 1713} = nc Using Progression PR;
//+
Transfinite Curve {1701, 1700, 1696, 1702} = nc Using Progression PR;
//+
Transfinite Curve {1727, 1721, 1712, 1726} = nc Using Progression PR;
//+
Transfinite Curve {1712, 1713, 1707, 1711} = nc Using Progression PR;
//+
Transfinite Curve {1707, 1702, 1697, 1706} = nc Using Progression PR;
//+
Transfinite Curve {1758, 1752, 1756, 1757} = nc Using Progression PR;
//+
Transfinite Curve {1752, 1753, 1747, 1751} = nc Using Progression PR;
//+
Transfinite Curve {1747, 1748, 1742, 1746} = nc Using Progression PR;
//+
Transfinite Curve {1742, 1741, 1737, 1743} = nc Using Progression PR;
//+
Transfinite Curve {1737, 1736, 1735, 1738} = nc Using Progression PR;
//+
Transfinite Curve {1756, 1751, 1767, 1771} = nc Using Progression PR;
//+
Transfinite Curve {1767, 1746, 1762, 1766} = nc Using Progression PR;
//+
Transfinite Curve {1762, 1743, 1738, 1763} = nc Using Progression PR;
//+
Transfinite Curve {1695, 1696, 1697, 1698} = nc Using Progression PR;
//+
Transfinite Surface {1694};
//+
Transfinite Surface {1699};
//+
Transfinite Surface {1714};
//+
Transfinite Surface {1719};
//+
Transfinite Surface {1704};
//+
Transfinite Surface {1709};
//+
Transfinite Surface {1724};
//+
Transfinite Surface {1729};
//+
Transfinite Surface {1734};
//+
Transfinite Surface {1739};
//+
Transfinite Surface {1744};
//+
Transfinite Surface {1749};
//+
Transfinite Surface {1754};
//+
Transfinite Surface {1769};
//+
Transfinite Surface {1764};
//+
Transfinite Surface {1759};
//+
Recombine Surface "*";
//+
out5[]=Extrude{{0,0,LE},{0,0,1},{0,0,0.25},0}{Surface{1694,1699,1714,1719,1704,1709,1724,1729,1734,1739,1744,1749,1754,1769,1764,1759};Layers{{2*FE*nx/3,FE*nx/3},{0.75,1}};Recombine;};
//+
Recombine Surface "*";
//+
//----------------------------------------------------------------------------------//
// Defining Physical Groups
//----------------------------------------------------------------------------------//
//
Physical Surface("inlet_gas") = {1694, 1699, 1714, 1719, 1704, 1709, 1724, 1729};
//+
Physical Surface("inlet_air") = {1734, 1739, 1744, 1749, 1754, 1769, 1764, 1759};
//+
Physical Surface("outlet") = {1248, 1253, 1263, 1258, 1243, 1306, 1307, 1308, 1238, 1233, 1228, 1304, 1305, 1283, 1288, 1278, 1273, 1268, 1293, 1298, 1303};
//+
Physical Surface("outer_wall") = {2071, 2037, 2050, 1928, 1780, 1801, 1830, 1851, 1919, 2020};
//+
Physical Surface("outer_wall") += {88, 110, 188, 210, 250, 264, 386, 400, 422, 360};
//+
Physical Surface("outer_wall") += {709, 739, 761, 829, 667, 650, 607, 539, 518, 676};
//+
Physical Surface("outer_wall") += {945, 928, 1009, 1039, 1061, 1159, 1180, 1205, 1227, 1082};
//+
Physical Surface("outer_wall") += {1332, 1391, 1353, 1362, 1578, 1464, 1439, 1552, 1634, 1693, 1659, 1672};
//+
Physical Surface("inner_wall") = {1932, 1881, 1953, 1982, 2003, 2024, 1864, 1792, 1898, 1915};
//+
Physical Surface("inner_wall") += {748, 791, 321, 409, 586, 608, 167, 189};
//+
Physical Surface("inner_wall") += {502, 482, 1129, 1206, 447, 452, 996, 1018};
//+
Physical Surface("inner_wall") += {1473, 1495, 1517, 1539, 1561};
//+
Physical Surface("blade_1") = {158, 224, 246, 136, 100, 364, 342, 290, 268, 320};
//+
Physical Surface("blade_2") = {680, 722, 790, 812, 833, 663, 621, 577, 560, 530};
//+
Physical Surface("blade_3") = {1078, 995, 1099, 1120, 1142, 1171, 1052, 1065, 974, 932};
//+
Physical Volume("fluid") = {83, 82, 81, 80, 79, 85, 84, 78, 70, 74, 75, 76, 77, 73, 72, 71, 16, 15, 14, 9, 10, 11, 12, 13, 1, 3, 4, 7, 8, 6, 5, 2};
//+
Physical Volume("fluid") += {28, 29, 32, 31, 30, 27, 26, 25, 17, 19, 20, 22, 24, 23, 21, 18, 41, 33, 34, 35, 42, 48, 47, 46, 45, 44, 43, 36, 39, 40, 38, 37, 68, 67, 62, 63, 64, 65, 69, 66, 61, 60, 59, 58, 57, 52, 53, 54, 55, 56, 51, 50, 49};
