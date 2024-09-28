//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {-0.01, 0, 0, 1.0};
//+
Point(3) = {0.01, 0, 0, 1.0};
//+
Point(4) = {0.01, -0.005, 0, 1.0};
//+
Point(5) = {0.0, -0.005, 0, 1.0};
//+
Point(6) = {-0.01, -0.005, 0, 1.0};
//+
Line(1) = {6, 2};
//+
Line(2) = {5, 1};
//+
Line(3) = {4, 3};
//+
Line(4) = {2, 1};
//+
Line(5) = {1, 3};
//+
Line(6) = {6, 5};
//+
Line(7) = {5, 4};
//+
Curve Loop(1) = {1, 4, -2, -6};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {5, -3, -7, 2};
//+
Plane Surface(2) = {2};
//+
Physical Curve("inlet", 8) = {1};
//+
Physical Curve("outlet", 9) = {3};
//+
Physical Curve("side_3", 10) = {6, 7};
//+
Physical Curve("cht_interface_3_1", 11) = {4};
//+
Physical Curve("cht_interface_3_2", 12) = {5};
//+
Physical Surface("fluid", 13) = {1, 2};
//+
Transfinite Curve {1, 2, 3} = 20 Using Progression 0.8;
//+
Transfinite Curve {4, 6, 7, 5} = 80 Using Progression 1;
//+
Transfinite Surface {1} = {6, 5, 1, 2};
//+
Transfinite Surface {2} = {5, 4, 3, 1};
//+
Recombine Surface {1, 2};

Mesh 2;

Save "fluid_mesh.su2";