//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {0.005, 0, 0, 1.0};
//+
Point(3) = {0.005, 0.03, 0, 1.0};
//+
Point(4) = {0, 0.03, 0, 1.0};
//+
Point(5) = {0, 0.0125, 0, 1.0};
//+
Point(6) = {-0.1, 0.0125, 0, 1.0};
//+
Point(7) = {-0.1, 0.0, 0, 1.0};
//+
Point(8) = {0.005, 0.0125, 0, 1.0};
//+
Point(9) = {0.32, 0.0, 0, 1.0};
//+
Point(10) = {0.32, 0.0125, 0, 1.0};
//+
Point(11) = {0.32, 0.03, 0, 1.0};
//+
Point(12) = {0.0, 0.0375, 0, 1.0};
//+
Point(13) = {0.005, 0.0375, 0, 1.0};
//+
Point(14) = {0.32, 0.0375, 0, 1.0};
//+
Line(1) = {7, 6};
//+
Line(2) = {1, 7};
//+
Line(3) = {1, 5};
//+
Line(4) = {5, 6};
//+
Line(5) = {1, 2};
//+
Line(6) = {2, 8};
//+
Line(7) = {5, 8};
//+
Line(8) = {4, 5};
//+
Line(9) = {4, 3};
//+
Line(10) = {3, 8};
//+
Line(11) = {2, 9};
//+
Line(12) = {8, 10};
//+
Line(13) = {3, 11};
//+
Line(14) = {9, 10};
//+
Line(15) = {11, 10};
//+
Line(16) = {12, 13};
//+
Line(17) = {13, 14};
//+
Line(18) = {12, 4};
//+
Line(19) = {13, 3};
//+
Line(20) = {14, 11};
//+
Curve Loop(1) = {-2, 3, 4, -1};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {5, 6, -7, -3};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {-7, -8, 9, 10};
//+
Plane Surface(3) = {3};
//+
Curve Loop(4) = {11, 14, -12, -6};
//+
Plane Surface(4) = {4};
//+
Curve Loop(5) = {12, -15, -13, 10};
//+
Plane Surface(5) = {5};
//+
Curve Loop(6) = {9, -19, -16, 18};
//+
Plane Surface(6) = {6};
//+
Curve Loop(7) = {-20, -17, 19, 13};
//+
Plane Surface(7) = {7};
//+
Physical Curve("inlet", 11) = {1};
Physical Curve("outlet", 12) = {14, 15, 20};
Physical Curve("wall_top", 13) = {16,17};
Physical Curve("wall_side", 14) = {8,18};
Physical Curve("wall_pipe", 15) = {4};
Physical Curve("symmetry", 16) = {2, 5, 11};
Physical Surface("interior", 17) = {1, 2, 3, 4, 5, 6, 7};
//+
Transfinite Curve {2, 4} = 40 Using Progression 1.1;
Transfinite Curve {5, 7, 9, 16} = 20 Using Progression 1.04;
Transfinite Curve {11, 12, 13, 17} = 150 Using Progression 1.015;
Transfinite Curve {1, 3} = 30 Using Progression 0.96;
Transfinite Curve {6, 14} = 30 Using Progression 1.0;
Transfinite Curve {8, 10, 15} = 30 Using Progression 1.0;
Transfinite Curve {18, 19, 20} = 30 Using Progression 1.05;
//+
Transfinite Surface {1};
Transfinite Surface {2};
Transfinite Surface {3};
Transfinite Surface {4};
Transfinite Surface {5};
Transfinite Surface {6};
Transfinite Surface {7};
//+
Recombine Surface {1, 2, 3, 4, 5, 6, 7};
