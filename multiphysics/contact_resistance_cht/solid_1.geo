//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {-0.01, 0, 0, 1.0};
//+
Point(3) = {-0.01, 0.01, 0, 1.0};
//+
Point(4) = {0, 0.01, 0, 1.0};
//+
Line(1) = {2, 3};
//+
Line(2) = {3, 4};
//+
Line(3) = {4, 1};
//+
Line(4) = {1, 2};
//+
Curve Loop(1) = {1, 2, 3, 4};
//+
Plane Surface(1) = {1};
//+
Physical Curve("isothermal_wall_1", 5) = {1};
//+
Physical Curve("cht_interface_1_2", 6) = {3};
//+
Physical Curve("side_1", 7) = {2};
//+
Physical Curve("cht_interface_1_3", 8) = {4};
//+
Physical Surface("solid_1", 9) = {1};
//+
Transfinite Curve {1, 2, 3, 4} = 40 Using Progression 1;
//+
Transfinite Surface {1} = {2, 1, 4, 3};
//+
Recombine Surface {1};
//+
Recombine Surface {1};

Mesh 2;

Save "solid_mesh_1.su2";