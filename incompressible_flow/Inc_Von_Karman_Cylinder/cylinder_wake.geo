D = 0.005;
L = 30*D;


X = 150*D;

//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {+L, 0, 0, 1.0};
Point(3) = {-L, 0, 0, 1.0};
//+
Point(4) = {0, +L, 0, 1.0};
Point(5) = {0, -L, 0, 1.0};
//+
Point(6) = {0, -D, 0, 1.0};
Point(7) = {0, +D, 0, 1.0};
//+
Point(8) = {+D, .0, 0, 1.0};
Point(9) = {-D, .0, 0, 1.0};

Point(10) = {L, +L, 0, 1.0};
Point(11) = {L, -L, 0, 1.0};

R = 0.5*D;
Point(12) = {R*2^0.5, R*2^0.5, 0, 1.0};
Point(13) = {R*2^0.5, -R*2^0.5, 0, 1.0};

Point(14) = {X, +L, 0, 1.0};
Point(15) = {X, -L, 0, 1.0};
Point(16) = {X, 0, 0, 1.0};


//+ upper right
Circle(1) = {7, 1, 12};
Circle(2) = {8, 1,12};
//+ lower right
Circle(3) = {8, 1, 13};
Circle(4) = {13, 1, 6};
//+ lower left
Circle(5) = {6, 1, 9};
//+ upper left
Circle(6) = {9, 1, 7};

//+
Circle(7) = {5, 1, 3};
//+
Circle(8) = {3, 1, 4};

//+
Line(10) = {8, 2};
//+
Line(11) = {7, 4};
//+
Line(12) = {9, 3};
//+
Line(13) = {6, 5};

Line(14) = {12, 10};
Line(15) = {13, 11};

//+
Line(16) = {4, 10};
//+
Line(17) = {5, 11};
//+
Line(18) = {2, 10};
//+
Line(19) = {2, 11};


//+
Line(20) = {10, 14};
//+
Line(21) = {2, 16};
//+
Line(22) = {11, 15};
//+
Line(23) = {16, 15};
//+
Line(24) = {16, 14};
//+
Curve Loop(1) = {12, 8, -11, -6};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {7, -12, -5, 13};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {11, 16, -14, -1};
//+
Plane Surface(3) = {3};
//+
Curve Loop(4) = {13, 17, -15, 4};
//+
Plane Surface(4) = {4};
//+
Curve Loop(5) = {14, -18, -10, 2};
//+
Plane Surface(5) = {5};
//+
Curve Loop(6) = {15, -19, -10, 3};
//+
Plane Surface(6) = {6};
//+
Curve Loop(7) = {-18, 21, 24, -20};
//+
Plane Surface(7) = {7};
//+
Curve Loop(8) = {19, 22, -23, -21};
//+
Plane Surface(8) = {8};
//+
Transfinite Curve {8, 6, 7, 5} = 40 Using Progression 1;
//+
Transfinite Curve {1, 16, 4, 17} = 40 Using Progression 1;
//+
Transfinite Curve {2, 3} = 80 Using Progression 1.00;
Transfinite Curve {18, 19} = 80 Using Progression 1.02;
Transfinite Curve {23, 24} = 80 Using Progression 1.01;
//+
Transfinite Curve {20, 21, 22} = 180 Using Progression 1;
//+
Transfinite Curve {10, 14, 11, 12, 13, 15} = 150 Using Progression 1.02;
//+
Transfinite Surface {1};
//+
Transfinite Surface {2};
//+
Transfinite Surface {4};
//+
Transfinite Surface {6};
//+
Transfinite Surface {5};
//+
Transfinite Surface {3};
//+
Transfinite Surface {7};
//+
Transfinite Surface {8};
//+
Recombine Surface {1, 2, 4, 6, 5, 3, 7, 8};
//+
Physical Curve("farfield_in", 25) = {8, 7};
//+
Physical Curve("farfield_side", 26) = {16, 17, 22, 20};
//+
Physical Curve("farfield_out", 27) = {24, 23};
//+
Physical Curve("cylinder", 28) = {6, 1, 2, 3, 4, 5};
//+
Physical Surface("interior", 29) = {1, 2, 4, 6, 5, 3, 7, 8};
