//+
Point(1) = {0, 0, 0, 1.0};
Point(2) = {0.18, 0, 0, 1.0};
Point(3) = {0.18, 0.0375, 0, 1.0};
Point(4) = {0, 0.0375, 0, 1.0};
Point(5) = {0, 0.0125, 0, 1.0};
Point(6) = {-0.1, 0.0125, 0, 1.0};
Point(7) = {-0.1, 0.0, 0, 1.0};
Point(8) = {0.18, 0.008, -0, 1.0};
Point(9) = {-0.05, 0.0, 0, 1.0};
Point(10) = {-0.05, 0.0125, 0, 1.0};
Point(11) = {0.40, 0.0, 0, 1.0};
Point(12) = {0.40, 0.0375, 0, 1.0};
Point(13) = {0.40, 0.008, 0, 1.0};
//+
Line(1) = {7, 6};
Line(2) = {1, 9};
Line(3) = {1, 5};
Line(4) = {5,10};
Line(5) = {1, 2};
Line(6) = {2, 8};
Line(7) = {5, 8};
Line(8) = {5, 4};
Line(9) = {4, 3};
Line(10) = {3, 8};
Line(11) = {9,10};
Line(12) = {7,9};
Line(13) = {6,10};

Line(14) = {11,13};
Line(15) = {13,12};
Line(16) = {2,11};
Line(17) = {8,13};
Line(18) = {3,12};
//+
Curve Loop(1) = {13, -11, -12, 1};
Plane Surface(1) = {1};
//+
Curve Loop(2) = {5, 6, -7, -3};
Plane Surface(2) = {2};
//+
Curve Loop(3) = {-7, 8, 9, 10};
Plane Surface(3) = {3};
//+
Curve Loop(4) = {4, -11, -2, 3};
Plane Surface(4) = {4};
//+
Curve Loop(5) = {17, 15, -18, 10};
Plane Surface(5) = {5};
//+
Curve Loop(6) = {16, 14, -17, -6};
Plane Surface(6) = {6};
//+
Physical Curve("inlet", 11) = {1};
Physical Curve("outlet", 12) = {14, 15};
Physical Curve("wall_top", 13) = {9,18};
Physical Curve("wall_side", 14) = {8};
Physical Curve("wall_pipe", 15) = {4,13};
Physical Curve("symmetry", 16) = {2, 5, 12,16};
//+
Physical Surface("interior", 17) = {1, 2, 3, 4,5,6};
//+
Transfinite Curve {2, 4} = 80 Using Progression 1.03;
//+
Transfinite Curve {5, 7, 9} = 200 Using Progression 1.01;
//+
Ny = 40;
Transfinite Curve {1, 3, 11} = Ny Using Progression 0.91;
Transfinite Curve {6} = Ny Using Progression 1.0;
Transfinite Curve {14} = Ny Using Progression 1.0;
//+
Transfinite Curve { 8} = 50 Using Progression 1.08;
Transfinite Curve {10} = 50 Using Progression 1;
Transfinite Curve {15} = 50 Using Progression 1;
Transfinite Curve {12, 13} = 40 Using Progression 1;
Transfinite Curve {16, 17, 18} = 100 Using Progression 1.005;
//+
Transfinite Surface {1};
Transfinite Surface {2};
Transfinite Surface {3};
Transfinite Surface {4};
Transfinite Surface {5};
Transfinite Surface {6};
//+
Recombine Surface {1, 3, 2, 4, 5, 6};
