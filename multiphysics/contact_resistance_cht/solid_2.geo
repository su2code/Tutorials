//+
Point(1) = {0, 0, 0, 1.0};
//+
Point(2) = {0.01, 0, 0, 1.0};
//+
Point(3) = {0.01, 0.01, 0, 1.0};
//+
Point(4) = {0.0, 0.01, 0, 1.0};
//+
Line(1) = {1, 4};
//+
Line(2) = {4, 3};
//+
Line(3) = {3, 2};
//+
Line(4) = {2, 1};
//+
Curve Loop(1) = {1, 2, 3, 4};
//+
Surface(1) = {1};
//+
Physical Curve("cht_interface_2_1", 5) = {1};
//+
Physical Curve("cht_interface_2_3", 6) = {4};
//+
Physical Curve("isothermal_wall_2", 7) = {3};
//+
Physical Curve("side_2", 8) = {2};
//+
Physical Surface("solid_2", 9) = {1};
//+
Transfinite Curve {1, 4, 3, 2} = 40 Using Progression 1;
//+
Transfinite Surface {1} = {1, 2, 3, 4};
//+
Recombine Surface {1};

Mesh 2;

Save "solid_mesh_2.su2";