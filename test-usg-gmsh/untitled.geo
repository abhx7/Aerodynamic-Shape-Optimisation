//+
Point(1) = {-0, -0, 1, 1.0};
//+
Point(2) = {0.7, 0.3, 1, 1.0};
//+
Point(3) = {1, 0.3, 1, 1.0};
//+
Point(4) = {1, 0.4, 1, 1.0};
//+
Point(5) = {0.7, 0.4, 1, 1.0};
//+
Point(6) = {-0.3, 0.4, 0.9, 1.0};
//+
Point(7) = {0.7, 0.6, 1, 1.0};
//+
Point(8) = {0, 0.6, 1, 1.0};
//+
Line(1) = {1, 2};
//+
Line(2) = {2, 3};
//+
Line(3) = {3, 4};
//+
Line(4) = {4, 5};
//+
Line(5) = {5, 7};
//+
Line(6) = {7, 8};
//+
Line(7) = {8, 1};
//+
Recursive Delete {
  Point{6}; 
}
//+
Recursive Delete {
  Curve{7}; Curve{6}; Curve{1}; Curve{2}; Curve{3}; Curve{4}; Curve{5}; 
}
//+
Point(1) = {-0, -0, 0, 1.0};
//+
Point(2) = {0.7, -0, 0, 1.0};
//+
Point(3) = {0.7, 0.3, 0, 1.0};
//+
Point(4) = {1, 0.3, 0, 1.0};
//+
Point(5) = {1, 0.4, 0, 1.0};
//+
Point(6) = {0.7, 0.4, 0, 1.0};
//+
Point(7) = {0.7, 0.6, 0, 1.0};
//+
Point(8) = {-0, 0.6, 0, 1.0};
//+
Line(1) = {1, 3};
//+
Line(2) = {4, 5};
//+
Line(3) = {3, 4};
//+
Line(4) = {5, 6};
//+
Line(5) = {6, 7};
//+
Line(6) = {7, 8};
//+
Line(7) = {8, 1};
//+
Curve Loop(1) = {7, 1, 3, 2, 4, 5, 6};
//+
Plane Surface(1) = {1};
//+
Plane Surface(2) = {1};
//+
Plane Surface(3) = {1};
//+
Plane Surface(4) = {1};
//+
Plane Surface(5) = {1};
//+
Plane Surface(6) = {1};
//+
Plane Surface(7) = {1};
//+
Physical Curve("body", 8) = {3, 1};
//+
Physical Curve("body", 8) += {1, 3};
