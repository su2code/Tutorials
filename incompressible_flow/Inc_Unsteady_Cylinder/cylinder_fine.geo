//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {1, 0, 0, 1.0};
//+
Point(3) = {-1, 0, 0, 1.0};
//+
Point(4) = {0, 1, 0, 1.0};
//+
Point(5) = {0, -1, 0, 1.0};
//+
Point(6) = {0, -.005, 0, 1.0};
//+
Point(7) = {0, .005, 0, 1.0};
//+
Point(8) = {0.005, .0, 0, 1.0};
//+
Point(9) = {-0.005, .0, 0, 1.0};
//+
Circle(1) = {7, 1, 8};
//+
Circle(2) = {8, 1, 6};
//+
Circle(4) = {6, 1, 9};
//+
Circle(5) = {9, 1, 7};
//+
Circle(6) = {4, 1, 2};
//+
Circle(7) = {2, 1, 5};
//+
Circle(8) = {5, 1, 3};
//+
Circle(9) = {3, 1, 4};
//+
Line(10) = {8, 2};
//+
Line(11) = {7, 4};
//+
Line(12) = {9, 3};
//+
Line(13) = {6, 5};
//+
Curve Loop(1) = {11, 6, -10, -1};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {2, 13, -7, -10};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {4, 12, -8, -13};
//+
Plane Surface(3) = {3};
//+
Curve Loop(4) = {5, 11, -9, -12};
//+
Plane Surface(4) = {4};
//+
Transfinite Curve {12, 11} = 200 Using Progression 1.03;
//+
Transfinite Curve {11, 10} = 200 Using Progression 1.03;
//+
Transfinite Curve {10, 13} = 200 Using Progression 1.03;
//+
Transfinite Curve {13, 12} = 200 Using Progression 1.03;
//+
Transfinite Curve {9, 5} = 200 Using Progression 1.0;
//+
Transfinite Curve {6, 1} = 200 Using Progression 1.0;
//+
Transfinite Curve {7, 2} = 200 Using Progression 1;
//+
Transfinite Curve {8, 4} = 200 Using Progression 1;
//+
Transfinite Surface {1};
//+
Transfinite Surface {2};
//+
Transfinite Surface {3};
//+
Transfinite Surface {4};
//+
Recombine Surface {1, 2, 3, 4};
//+
Physical Curve("farfield") = {9, 6, 7, 8};
//+
Physical Curve("wall") = {5, 1, 2, 4};
//+
Physical Surface("interior") = {4, 1, 2, 3};
