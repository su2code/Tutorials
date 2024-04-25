domain_width=0.0008;
hex_center=0.002;
hex_radius=0.0003;

//+
Point(1) = {-0.003, 0, 0, 1.0};
//+
Point(2) = {-0.003, domain_width, 0, 1.0};
//+
Point(3) = {-0.001, domain_width, 0, 1.0};
//+
Point(4) = {-0.001, 0.5*domain_width, 0, 1.0};
//+
Point(5) = {-0.00, 0.5*domain_width, 0, 1.0};
//+
Point(6) = {-0.00, domain_width, 0, 1.0};
//+
Point(7) = {0.005, domain_width, 0, 1.0};
//+
Point(8) = {0.005, 0.000, 0, 1.0};
//+
Point(9) = {hex_center, 0.000, 0, 1.0};
//+
Point(10) = {hex_center+hex_radius, 0.000, 0, 1.0};
//+
Point(11) = {hex_center-hex_radius, 0.000, 0, 1.0};
//+
Line(1) = {2, 1};
//+
Line(2) = {2, 3};
//+
Line(3) = {3, 4};
//+
Line(4) = {4, 5};
//+
Line(5) = {5, 6};
//+
Line(6) = {6, 7};
//+
Line(7) = {7, 8};
//+
Line(8) = {10, 8};
//+
Line(9) = {1, 11};
//+
Circle(10) = {10, 9, 11};
//+
Curve Loop(1) = {1, 9, -10, 8, -7, -6, -5, -4, -3, -2};
//+
Plane Surface(1) = {1};
//+
//Physical Curve("inlet", 11) = {1};
//+
//Physical Curve("outlet", 12) = {7};
//+
//Physical Curve("burner_wall", 13) = {3, 4, 5};
//+
//Physical Curve("cylinder_wall", 14) = {10};
//+
//Physical Curve("sides", 15) = {2, 9, 6, 8};
//+
//Physical Surface("fluid", 16) = {1};
//+
Transfinite Curve {1, 7} = 30 Using Progression 1;
//+
Transfinite Curve {3, 5} = 30 Using Progression 1;
//+
Transfinite Curve {4} = 80 Using Progression 1;
//+
Transfinite Curve {2} = 100 Using Progression 1;
//+
Transfinite Curve {6} = 300 Using Progression 1;
//+
Transfinite Curve {8} = 200 Using Progression 1;
//+
Transfinite Curve {9} = 350 Using Progression 1;
//+
Transfinite Curve {10} = 100 Using Progression 1;

//Mesh 2;

//Save "H2_burner.su2";//+
Extrude {{1, 0, 0}, {0, -0.001, 0}, Pi/8} {
  Surface{1}; Layers{10}; Recombine;
}
//+
Physical Surface("inlet", 63) = {25};
//+
Physical Surface("outlet", 64) = {41};
//+
Physical Surface("sides", 65) = {62, 29, 61, 1, 45, 37};
//+
Physical Surface("burner_wall", 66) = {57, 53, 49};
//+
Physical Surface("cylinder_wall", 67) = {33};
//+
Physical Volume("fluid", 68) = {1};
