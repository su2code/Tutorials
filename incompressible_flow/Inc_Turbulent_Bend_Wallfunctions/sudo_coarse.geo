//+
SetFactory("OpenCASCADE");

// setup of 90 degree pipe bend (Sudo,1998)
// Diameter of the pipe 104 mm (Sudo,1998)
D = 0.104;
R = 0.5*D;
// curvature radius of the bend (Sudo,1998)
// Rc = 208mm = 2*D = 4*R
Rc = 4; 
X = 0.7071078 * R;
//Sudo: 100D
//L_upstream = 100*D;
// 50D Dutta
L_upstream = 5*D;
//Sudo: 40D
//L_downstream = 40*D;
// Dutta: 20D
L_downstream = 10*D;

// coarse
N1 = 20;
Nbend = 30;
N2 =50;
L1=10;
L2=12;

// size of the square
Xs = 0.8 * X;

//+
// square
Point(1) = {-1.40*Xs, -Xs, 0, 1.0};
Point(2) = {+1.40*Xs, -Xs, 0, 1.0};
Point(3) = {+Xs, +Xs, 0, 1.0};
Point(4) = {-Xs, +Xs, 0, 1.0};

// center point
Point(5) = {0.0, 0.0, 0, 1.0};

// points on circle (making a square)
Point(6) = {-X, -X, 0, 1.0};
Point(7) = {+X, -X, 0, 1.0};
Point(8) = {+X, +X, 0, 1.0};
Point(9) = {-X, +X, 0, 1.0};
//+
Line(1) = {1, 2};
//+
Line(2) = {2, 3};
//+
Line(3) = {3, 4};
//+
Line(4) = {4, 1};
//+
Circle(5) = {9, 5, 8};
//+
Circle(6) = {8, 5, 7};
//+
Circle(7) = {7, 5, 6};
//+
Circle(8) = {6, 5, 9};
//+
Line(9) = {3, 8};
//+
Line(10) = {2, 7};
//+
Line(11) = {1, 6};
//+
Line(12) = {4, 9};
//+
//+
Rectangle(1) = {-5, -5, 0, 10, 5, 0};
//+
Curve Loop(2) = {9, 6, -10, 2};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {5, -9, 3, 12};
//+
Plane Surface(3) = {3};
//+
Curve Loop(4) = {8, -12, 4, 11};
//+
Plane Surface(4) = {4};
//+
Curve Loop(5) = {7, -11, 1, 10};
//+
Plane Surface(5) = {5};
//+
Curve Loop(6) = {1, 2, 3, 4};
//+
Plane Surface(6) = {6};
//+
BooleanDifference{ Surface{2}; Surface{4}; Surface{5}; Surface{6}; Surface{3};Delete; }{ Surface{1}; Delete; }
//+
Transfinite Curve {13, 15, 17, 18} = L1 Using Progression 1.0;
//+
Transfinite Curve {3, 5, 19} = 2*L1 Using Progression 1.0;
//+
Transfinite Curve {-14, 9, 12, 16} = L2 Using Progression 0.90;
//+
Transfinite Surface {2};
//+
Transfinite Surface {3};
//+
Transfinite Surface {4};
//+
Transfinite Surface {6};
//+
Recombine Surface {2, 3, 4, 6};
//+
// upstream part: 100D
// note that we extrude with different extrusion steps
// N1
Extrude {0, 0, -L_upstream} {
  Surface{3}; Surface{4}; Surface{6}; Surface{2}; Layers{{6,6,25},{0.1,0.25,1}}; Recombine;
}
// make the bend 
Extrude {{0, 1, 0}, {4*R, 0, 0}, Pi/2} {
  Surface{3}; Surface{4}; Surface{6}; Surface{2}; Layers{Nbend}; Recombine;
}
//+
// N2 Layers{{x1,x2,x3},{y1,y2,1.0}} means we have x1 layers from [0.0 - y1], then x2 layers from [y1 - y2], then x3 layers from [y2-1.0]
Extrude {L_downstream, 0, 0} {
  Surface{26}; Surface{30}; Surface{33}; Surface{36}; Layers{{12,12,30},{0.10,0.25,1}}; Recombine;
}
//+
Physical Surface("inlet") = {21, 11, 18, 15};
//+
Physical Surface("outlet") = {51, 41, 48, 45};
//+
Physical Surface("wall_2") = {44, 37, 50};
//+
Physical Surface("wall_bend") = {35, 22, 29};
//+
Physical Surface("wall_1") = {20, 7, 14};
//+
Physical Surface("symmetry_1") = {12, 17, 19};
//+
Physical Surface("symmetry_bend") = {27, 32, 34};
//+
Physical Surface("symmetry_2") = {42, 47, 49};
//+
Physical Volume("volume") = {2, 1, 3, 4, 6, 5, 7, 8, 10, 9, 11, 12};
