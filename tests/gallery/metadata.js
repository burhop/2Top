window.SCENE_METADATA = [
  {
    "id": "scene_001",
    "name": "Unit Circle",
    "description": "A standard unit circle centered at the origin.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 83.81,
    "scene_file": "scenes/scene_001.json",
    "image_file": "images/scene_001.png",
    "scene_data": {
      "objects": {
        "circle": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "circle": {
          "color": "#1f77b4",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:56.183681",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_002",
    "name": "Ellipse (a=3, b=1)",
    "description": "An axis-aligned ellipse centered at the origin.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 65.99,
    "scene_file": "scenes/scene_002.json",
    "image_file": "images/scene_002.png",
    "scene_data": {
      "objects": {
        "ellipse": {
          "type": "ConicSection",
          "expression": "x**2/9 + y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "ellipse"
        }
      },
      "styles": {
        "ellipse": {
          "color": "#9467bd",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:56.285544",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_003",
    "name": "Upward Parabola",
    "description": "Standard upward-opening parabola y - x^2 = 0.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 57.67,
    "scene_file": "scenes/scene_003.json",
    "image_file": "images/scene_003.png",
    "scene_data": {
      "objects": {
        "parabola": {
          "type": "ImplicitCurve",
          "expression": "-x**2 + y",
          "variables": [
            "x",
            "y"
          ]
        }
      },
      "styles": {
        "parabola": {
          "color": "#ff7f0e",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:56.367051",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_004",
    "name": "Diagonal Line",
    "description": "A straight diagonal line passing through the origin.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 62.88,
    "scene_file": "scenes/scene_004.json",
    "image_file": "images/scene_004.png",
    "scene_data": {
      "objects": {
        "line": {
          "type": "ImplicitCurve",
          "expression": "x - y",
          "variables": [
            "x",
            "y"
          ]
        }
      },
      "styles": {
        "line": {
          "color": "#2ca02c",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:56.445703",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_005",
    "name": "Standard Triangle",
    "description": "Triangle constructed from three connected line segments.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 129.21,
    "scene_file": "scenes/scene_005.json",
    "image_file": "images/scene_005.png",
    "scene_data": {
      "objects": {
        "triangle": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -0.5
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  -1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "triangle": {
          "color": "#d62728",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:56.521179",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_006",
    "name": "Square (2x2)",
    "description": "A 2x2 square boundary centered at the origin.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 128.57,
    "scene_file": "scenes/scene_006.json",
    "image_file": "images/scene_006.png",
    "scene_data": {
      "objects": {
        "square": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -1
                ],
                [
                  1,
                  -1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -1
                ],
                [
                  1,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  1
                ],
                [
                  -1,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  1
                ],
                [
                  -1,
                  -1
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1,
            1,
            -1,
            1
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "square": {
          "color": "#e377c2",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:56.672667",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_007",
    "name": "L-Shape Segment",
    "description": "L-shape constructed from two perpendicular segments.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 91.95,
    "scene_file": "scenes/scene_007.json",
    "image_file": "images/scene_007.png",
    "scene_data": {
      "objects": {
        "l_shape": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -1
                ],
                [
                  -0.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -1
                ],
                [
                  0.5,
                  -1
                ]
              ]
            }
          ],
          "segment_count": 2,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "l_shape": {
          "color": "#bcbd22",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:56.825856",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_008",
    "name": "T-Shape Segment",
    "description": "T-shape constructed from three connected perpendicular segments.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 104.08,
    "scene_file": "scenes/scene_008.json",
    "image_file": "images/scene_008.png",
    "scene_data": {
      "objects": {
        "t_shape": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  0.5
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  0,
                  -1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  1,
                  0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "t_shape": {
          "color": "#17becf",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:56.937785",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_009",
    "name": "Zigzag Segment",
    "description": "Zigzag pattern connecting multiple vertices.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 91.07,
    "scene_file": "scenes/scene_009.json",
    "image_file": "images/scene_009.png",
    "scene_data": {
      "objects": {
        "zigzag": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-x + y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 2,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "zigzag": {
          "color": "#8c564b",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:57.065618",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_010",
    "name": "Staircase Segment",
    "description": "Perpendicular staircase step pattern.",
    "complexity_tier": 1,
    "tier_name": "Simple Curves",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 138.32,
    "scene_file": "scenes/scene_010.json",
    "image_file": "images/scene_010.png",
    "scene_data": {
      "objects": {
        "staircase": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -1
                ],
                [
                  -0.5,
                  -1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -1
                ],
                [
                  -0.5,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -0.5
                ],
                [
                  0,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -0.5
                ],
                [
                  0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0
                ],
                [
                  0.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  0
                ],
                [
                  0.5,
                  0.5
                ]
              ]
            }
          ],
          "segment_count": 6,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "staircase": {
          "color": "#7f7f7f",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:57.174698",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_011",
    "name": "Figure Eight",
    "description": "Continuous closed figure-eight shape using circular arcs.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 129.05,
    "scene_file": "scenes/scene_011.json",
    "image_file": "images/scene_011.png",
    "scene_data": {
      "objects": {
        "figure_eight": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.5)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.5)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y + 0.5)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0
                ],
                [
                  0,
                  -1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y + 0.5)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -1
                ],
                [
                  0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "figure_eight": {
          "color": "#1f77b4",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:57.335897",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_012",
    "name": "D-Shape Hybrid",
    "description": "D-shape combining a semicircle with a straight boundary.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 93.54,
    "scene_file": "scenes/scene_012.json",
    "image_file": "images/scene_012.png",
    "scene_data": {
      "objects": {
        "d_shape": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -1.0
                ],
                [
                  0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1.0
                ],
                [
                  0,
                  -1.0
                ]
              ]
            }
          ],
          "segment_count": 2,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "d_shape": {
          "color": "#2ca02c",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:57.489220",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_013",
    "name": "Egg-Shape Hybrid",
    "description": "Egg-like hybrid shape combining ellipse and parabola arcs.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 100.44,
    "scene_file": "scenes/scene_013.json",
    "image_file": "images/scene_013.png",
    "scene_data": {
      "objects": {
        "egg_shape": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2/4 + y**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5723027555148466,
                  0.6180339887498949
                ],
                [
                  1.5723027555148466,
                  0.6180339887498949
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-x**2/4 + y",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 2
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5723027555148466,
                  0.6180339887498949
                ],
                [
                  -1.5723027555148466,
                  0.6180339887498949
                ]
              ]
            }
          ],
          "segment_count": 2,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "egg_shape": {
          "color": "#ff7f0e",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:57.601075",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_014",
    "name": "Concentric Circles",
    "description": "Two concentric circles of radius 1 and 2.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 71.2,
    "scene_file": "scenes/scene_014.json",
    "image_file": "images/scene_014.png",
    "scene_data": {
      "objects": {
        "circle1": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "circle2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 4.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "circle1": {
          "color": "#1f77b4"
        },
        "circle2": {
          "color": "#aec7e8"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:57.723758",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_015",
    "name": "Intersecting Circles",
    "description": "Two intersecting circles at x=-0.75 and x=0.75.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 75.51,
    "scene_file": "scenes/scene_015.json",
    "image_file": "images/scene_015.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 0.75)**2 - 1.5625",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 0.75)**2 - 1.5625",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#ff7f0e"
        },
        "c2": {
          "color": "#ffbb78"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:57.812338",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_016",
    "name": "Concentric Ellipses",
    "description": "Concentric ellipses with different semi-axes.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 75.46,
    "scene_file": "scenes/scene_016.json",
    "image_file": "images/scene_016.png",
    "scene_data": {
      "objects": {
        "e1": {
          "type": "ConicSection",
          "expression": "0.25*x**2 + 1.0*y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "ellipse"
        },
        "e2": {
          "type": "ConicSection",
          "expression": "0.0816326530612245*x**2 + 0.326530612244898*y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "ellipse"
        }
      },
      "styles": {
        "e1": {
          "color": "#9467bd"
        },
        "e2": {
          "color": "#c5b0d5"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:57.909572",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_017",
    "name": "Offset Squares",
    "description": "Two squares offset from the origin.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 183.64,
    "scene_file": "scenes/scene_017.json",
    "image_file": "images/scene_017.png",
    "scene_data": {
      "objects": {
        "sq1": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2,
                  -2
                ],
                [
                  0,
                  -2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -2
                ],
                [
                  0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0
                ],
                [
                  -2,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2,
                  0
                ],
                [
                  -2,
                  -2
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -2,
            0,
            -2,
            0
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq2": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0
                ],
                [
                  2,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2,
                  0
                ],
                [
                  2,
                  2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2,
                  2
                ],
                [
                  0,
                  2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  2
                ],
                [
                  0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            0,
            2,
            0,
            2
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "sq1": {
          "color": "#d62728"
        },
        "sq2": {
          "color": "#ff9896"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:58.003613",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_018",
    "name": "Parallel Lines",
    "description": "Two parallel diagonal lines.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 85.69,
    "scene_file": "scenes/scene_018.json",
    "image_file": "images/scene_018.png",
    "scene_data": {
      "objects": {
        "line1": {
          "type": "ImplicitCurve",
          "expression": "x - y - 1",
          "variables": [
            "x",
            "y"
          ]
        },
        "line2": {
          "type": "ImplicitCurve",
          "expression": "x - y + 1",
          "variables": [
            "x",
            "y"
          ]
        }
      },
      "styles": {
        "line1": {
          "color": "#2ca02c"
        },
        "line2": {
          "color": "#98df8a"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:58.211454",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_019",
    "name": "Intersecting Circle & Line",
    "description": "A unit circle intersected by a vertical line at x=0.5.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 104.86,
    "scene_file": "scenes/scene_019.json",
    "image_file": "images/scene_019.png",
    "scene_data": {
      "objects": {
        "circle": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 2.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "line": {
          "type": "ImplicitCurve",
          "expression": "x - 0.75",
          "variables": [
            "x",
            "y"
          ]
        }
      },
      "styles": {
        "circle": {
          "color": "#1f77b4"
        },
        "line": {
          "color": "#d62728"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:58.311055",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_020",
    "name": "Circle & Ellipse Cross",
    "description": "A circle and a stretched ellipse intersecting.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 72.88,
    "scene_file": "scenes/scene_020.json",
    "image_file": "images/scene_020.png",
    "scene_data": {
      "objects": {
        "circle": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 2.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "ellipse": {
          "type": "ConicSection",
          "expression": "0.111111111111111*x**2 + 1.77777777777778*y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "ellipse"
        }
      },
      "styles": {
        "circle": {
          "color": "#17becf"
        },
        "ellipse": {
          "color": "#bcbd22"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:58.431948",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_021",
    "name": "Triangle inside Circle",
    "description": "A triangle centered inside a larger outer circle.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 121.64,
    "scene_file": "scenes/scene_021.json",
    "image_file": "images/scene_021.png",
    "scene_data": {
      "objects": {
        "circle": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 6.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "triangle": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -0.5
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  -1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "circle": {
          "color": "#1f77b4"
        },
        "triangle": {
          "color": "#d62728"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:58.523661",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_022",
    "name": "Square inside Circle",
    "description": "A square nested inside an outer circle.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 130.62,
    "scene_file": "scenes/scene_022.json",
    "image_file": "images/scene_022.png",
    "scene_data": {
      "objects": {
        "circle": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 4.84",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "square": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -1
                ],
                [
                  1,
                  -1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -1
                ],
                [
                  1,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  1
                ],
                [
                  -1,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  1
                ],
                [
                  -1,
                  -1
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1,
            1,
            -1,
            1
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "circle": {
          "color": "#e377c2"
        },
        "square": {
          "color": "#7f7f7f"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:58.668724",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_023",
    "name": "Superellipse (n=3)",
    "description": "A superellipse curve with parameter exponent n=3.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 62.8,
    "scene_file": "scenes/scene_023.json",
    "image_file": "images/scene_023.png",
    "scene_data": {
      "objects": {
        "se": {
          "type": "Superellipse",
          "expression": "0.125*Abs(x)**3.0 + 0.296296296296296*Abs(y)**3.0 - 1",
          "variables": [
            "x",
            "y"
          ],
          "a": 2.0,
          "b": 1.5,
          "n": 3.0,
          "shape_type": "square-like"
        }
      },
      "styles": {
        "se": {
          "color": "#8c564b",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:58.828306",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_024",
    "name": "Three Circles",
    "description": "Three circles forming a triangular alignment.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 3,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 88.05,
    "scene_file": "scenes/scene_024.json",
    "image_file": "images/scene_024.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.0)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "(x + 1.0)**2 + (y + 0.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c3": {
          "type": "ConicSection",
          "expression": "(x - 1.0)**2 + (y + 0.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "c3": {
          "color": "#ff7f0e"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:58.909279",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_025",
    "name": "Double Parabola",
    "description": "Two parabolas opening in opposite directions.",
    "complexity_tier": 2,
    "tier_name": "Dual Shapes & Hybrids",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 74.35,
    "scene_file": "scenes/scene_025.json",
    "image_file": "images/scene_025.png",
    "scene_data": {
      "objects": {
        "p1": {
          "type": "ImplicitCurve",
          "expression": "-0.5*x**2 + y",
          "variables": [
            "x",
            "y"
          ]
        },
        "p2": {
          "type": "ImplicitCurve",
          "expression": "-0.5*x**2 - y + 2",
          "variables": [
            "x",
            "y"
          ]
        }
      },
      "styles": {
        "p1": {
          "color": "#ff7f0e"
        },
        "p2": {
          "color": "#aec7e8"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:59.015018",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_026",
    "name": "Flower (3 petals)",
    "description": "Multi-conic flower shape with 3 alternating petals.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 127.7,
    "scene_file": "scenes/scene_026.json",
    "image_file": "images/scene_026.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(0.499999999999999*x - 0.866025403784439*y + 0.8)**2 + 25.0*(0.866025403784439*x + 0.499999999999999*y + 4.44089209850063e-16)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.4)**2 + (y + 0.692820323027551)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#d62728",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:59.109999",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_027",
    "name": "Flower (4 petals)",
    "description": "Multi-conic flower shape with 4 alternating petals.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 145.61,
    "scene_file": "scenes/scene_027.json",
    "image_file": "images/scene_027.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-1.83697019872103e-16*x - 1.0*y + 0.8)**2 + 25.0*(1.0*x - 1.83697019872103e-16*y + 9.79717439317882e-17)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.8)**2 + (y - 9.79717439317883e-17)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 1.46957615897682e-16)**2 + (y + 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#9467bd",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:59.260234",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_028",
    "name": "Flower (5 petals)",
    "description": "Multi-conic flower shape with 5 alternating petals.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 177.4,
    "scene_file": "scenes/scene_028.json",
    "image_file": "images/scene_028.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.309016994374948*x - 0.951056516295154*y + 0.8)**2 + 25.0*(0.951056516295154*x - 0.309016994374948*y + 8.32667268468867e-17)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.647213595499958)**2 + (y - 0.470228201833979)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.647213595499958)**2 + (y + 0.470228201833978)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.951056516295154*x - 0.309016994374947*y + 8.32667268468867e-17)**2 + 4.0*(-0.309016994374947*x + 0.951056516295154*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 5,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#e377c2",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:59.432947",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_029",
    "name": "Flower (6 petals)",
    "description": "Multi-conic flower shape with 6 alternating petals.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 223.09,
    "scene_file": "scenes/scene_029.json",
    "image_file": "images/scene_029.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.5*x - 0.866025403784438*y + 0.8)**2 + 25.0*(0.866025403784438*x - 0.5*y + 2.77555756156289e-16)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.4)**2 + (y - 0.692820323027551)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.8)**2 + (y - 9.79717439317883e-17)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.866025403784438*x + 0.5*y + 5.55111512312578e-17)**2 + 4.0*(0.5*x + 0.866025403784438*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.4)**2 + (y + 0.692820323027551)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 6,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#17becf",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:59.640289",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_030",
    "name": "Spiral (1 turn)",
    "description": "Spiral approximation using quarter-circle segments (1 full turn).",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 132.99,
    "scene_file": "scenes/scene_030.json",
    "image_file": "images/scene_030.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.208333333333333)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.7916666666666666,
                  0.20833333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.208333333333333)**2 + (y - 0.208333333333333)**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.7916666666666666,
                  0.20833333333333337
                ],
                [
                  -0.20833333333333337,
                  -0.3749999999999999
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.208333333333333)**2 + (y - 1.11022302462516e-16)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.20833333333333337,
                  -0.3749999999999999
                ],
                [
                  0.16666666666666663,
                  1.1102230246251565e-16
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:44:59.888239",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_031",
    "name": "Spiral (2 turns)",
    "description": "Spiral approximation using quarter-circle segments (2 full turns).",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 201.12,
    "scene_file": "scenes/scene_031.json",
    "image_file": "images/scene_031.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.104166666666667)**2 - 0.802517361111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.8958333333333334,
                  0.10416666666666663
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.104166666666667)**2 + (y - 0.104166666666667)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8958333333333334,
                  0.10416666666666663
                ],
                [
                  -0.10416666666666674,
                  -0.6875
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.104166666666667)**2 - 0.47265625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.10416666666666674,
                  -0.6875
                ],
                [
                  0.5833333333333333,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5833333333333333,
                  0.0
                ],
                [
                  0.0,
                  0.5833333333333333
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.104166666666667)**2 - 0.229600694444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.5833333333333333
                ],
                [
                  -0.47916666666666663,
                  0.10416666666666663
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.104166666666667)**2 + (y - 0.104166666666667)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.47916666666666663,
                  0.10416666666666663
                ],
                [
                  -0.10416666666666663,
                  -0.27083333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.104166666666667)**2 + (y + 1.11022302462516e-16)**2 - 0.0733506944444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.10416666666666663,
                  -0.27083333333333337
                ],
                [
                  0.16666666666666663,
                  -1.1102230246251565e-16
                ]
              ]
            }
          ],
          "segment_count": 8,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:00.035600",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_032",
    "name": "Spiral (3 turns)",
    "description": "Spiral approximation using quarter-circle segments (3 full turns).",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 257.94,
    "scene_file": "scenes/scene_032.json",
    "image_file": "images/scene_032.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0694444444444444)**2 - 0.865933641975309",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.9305555555555556,
                  0.06944444444444442
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y - 0.0694444444444444)**2 - 0.741512345679012",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.9305555555555556,
                  0.06944444444444442
                ],
                [
                  -0.06944444444444442,
                  -0.7916666666666667
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y + 1.11022302462516e-16)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.06944444444444442,
                  -0.7916666666666667
                ],
                [
                  0.7222222222222222,
                  -1.1102230246251565e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y + 1.11022302462516e-16)**2 - 0.521604938271605",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.7222222222222222,
                  -1.1102230246251565e-16
                ],
                [
                  0.0,
                  0.7222222222222221
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0694444444444444)**2 - 0.426118827160494",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.7222222222222221
                ],
                [
                  -0.6527777777777777,
                  0.06944444444444442
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y - 0.0694444444444444)**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.6527777777777777,
                  0.06944444444444442
                ],
                [
                  -0.06944444444444442,
                  -0.5138888888888888
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0694444444444444)**2 - 0.264081790123457",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.06944444444444442,
                  -0.5138888888888888
                ],
                [
                  0.4444444444444444,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 0.197530864197531",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.4444444444444444,
                  0.0
                ],
                [
                  0.0,
                  0.4444444444444444
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0694444444444445)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.4444444444444444
                ],
                [
                  -0.3749999999999999,
                  0.06944444444444453
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y - 0.0694444444444445)**2 - 0.0933641975308641",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3749999999999999,
                  0.06944444444444453
                ],
                [
                  -0.06944444444444442,
                  -0.23611111111111094
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y - 1.11022302462516e-16)**2 - 0.0557484567901234",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.06944444444444442,
                  -0.23611111111111094
                ],
                [
                  0.16666666666666663,
                  1.1102230246251565e-16
                ]
              ]
            }
          ],
          "segment_count": 12,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:00.262458",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_033",
    "name": "Superellipse-Circle Hybrid",
    "description": "Rounded square superellipse blended with circular arcs.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 103.21,
    "scene_file": "scenes/scene_033.json",
    "image_file": "images/scene_033.png",
    "scene_data": {
      "objects": {
        "hybrid": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "Superellipse",
                "expression": "Abs(x)**4 + Abs(y)**4 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "a": 1.0,
                "b": 1.0,
                "n": 4.0,
                "shape_type": "square-like"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -1
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.5)**2 - 1.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  0,
                  -1
                ]
              ]
            }
          ],
          "segment_count": 2,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "hybrid": {
          "color": "#ff7f0e",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:00.539385",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_034",
    "name": "Heart Shape",
    "description": "Beautiful heart shape using two circular lobes and a parabolic base.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 118.65,
    "scene_file": "scenes/scene_034.json",
    "image_file": "images/scene_034.png",
    "scene_data": {
      "objects": {
        "heart": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  0
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  1,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-x**2 + y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 2
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  0
                ],
                [
                  -1,
                  0
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "heart": {
          "color": "#d62728",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:00.664256",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_035",
    "name": "House Shape",
    "description": "Square base with a triangular roof, forming a continuous path.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 134.54,
    "scene_file": "scenes/scene_035.json",
    "image_file": "images/scene_035.png",
    "scene_data": {
      "objects": {
        "house": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -1
                ],
                [
                  0.5,
                  -1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  -1
                ],
                [
                  0.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  0
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-x + y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  -0.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  0
                ],
                [
                  -0.5,
                  -1
                ]
              ]
            }
          ],
          "segment_count": 5,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "house": {
          "color": "#8c564b",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:00.808948",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_036",
    "name": "Nested Triangles",
    "description": "Three nested triangles of increasing sizes.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 3,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 223.86,
    "scene_file": "scenes/scene_036.json",
    "image_file": "images/scene_036.png",
    "scene_data": {
      "objects": {
        "tri_1": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -0.5
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  -1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "tri_2": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -0.5
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  -1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "tri_3": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -0.5
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  -1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "tri_1": {
          "color": "#2ca02c",
          "linewidth": 1.5
        },
        "tri_2": {
          "color": "#2ca02c",
          "linewidth": 3.0
        },
        "tri_3": {
          "color": "#2ca02c",
          "linewidth": 4.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:00.967995",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_037",
    "name": "Overlapping Squares Grid",
    "description": "Four overlapping squares forming a window pane alignment.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 4,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 327.29,
    "scene_file": "scenes/scene_037.json",
    "image_file": "images/scene_037.png",
    "scene_data": {
      "objects": {
        "sq1": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  -1.5
                ],
                [
                  0.5,
                  -1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  -1.5
                ],
                [
                  0.5,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  0.5
                ],
                [
                  -1.5,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  0.5
                ],
                [
                  -1.5,
                  -1.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.5,
            0.5,
            -1.5,
            0.5
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq2": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -1.5
                ],
                [
                  1.5,
                  -1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  -1.5
                ],
                [
                  1.5,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  0.5
                ],
                [
                  -0.5,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  0.5
                ],
                [
                  -0.5,
                  -1.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -0.5,
            1.5,
            -1.5,
            0.5
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq3": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  -0.5
                ],
                [
                  0.5,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  -0.5
                ],
                [
                  0.5,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  1.5
                ],
                [
                  -1.5,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  1.5
                ],
                [
                  -1.5,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.5,
            0.5,
            -0.5,
            1.5
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq4": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -0.5
                ],
                [
                  1.5,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  -0.5
                ],
                [
                  1.5,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  1.5
                ],
                [
                  -0.5,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  1.5
                ],
                [
                  -0.5,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -0.5,
            1.5,
            -0.5,
            1.5
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "sq1": {
          "color": "#aec7e8"
        },
        "sq2": {
          "color": "#ffbb78"
        },
        "sq3": {
          "color": "#98df8a"
        },
        "sq4": {
          "color": "#ff9896"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:01.216165",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_038",
    "name": "Spiral & Circle Nest",
    "description": "A 2-turn spiral centered within an outer bounding circle.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 209.84,
    "scene_file": "scenes/scene_038.json",
    "image_file": "images/scene_038.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.104166666666667)**2 - 0.802517361111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.8958333333333334,
                  0.10416666666666663
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.104166666666667)**2 + (y - 0.104166666666667)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8958333333333334,
                  0.10416666666666663
                ],
                [
                  -0.10416666666666674,
                  -0.6875
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.104166666666667)**2 - 0.47265625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.10416666666666674,
                  -0.6875
                ],
                [
                  0.5833333333333333,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5833333333333333,
                  0.0
                ],
                [
                  0.0,
                  0.5833333333333333
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.104166666666667)**2 - 0.229600694444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.5833333333333333
                ],
                [
                  -0.47916666666666663,
                  0.10416666666666663
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.104166666666667)**2 + (y - 0.104166666666667)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.47916666666666663,
                  0.10416666666666663
                ],
                [
                  -0.10416666666666663,
                  -0.27083333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.104166666666667)**2 + (y + 1.11022302462516e-16)**2 - 0.0733506944444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.10416666666666663,
                  -0.27083333333333337
                ],
                [
                  0.16666666666666663,
                  -1.1102230246251565e-16
                ]
              ]
            }
          ],
          "segment_count": 8,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 6.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22"
        },
        "circle": {
          "color": "#1f77b4",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:01.566299",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_039",
    "name": "Star Grid (4 Lines)",
    "description": "Four intersecting lines meeting at the origin.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 4,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 114.83,
    "scene_file": "scenes/scene_039.json",
    "image_file": "images/scene_039.png",
    "scene_data": {
      "objects": {
        "l1": {
          "type": "ImplicitCurve",
          "expression": "x",
          "variables": [
            "x",
            "y"
          ]
        },
        "l2": {
          "type": "ImplicitCurve",
          "expression": "y",
          "variables": [
            "x",
            "y"
          ]
        },
        "l3": {
          "type": "ImplicitCurve",
          "expression": "x - y",
          "variables": [
            "x",
            "y"
          ]
        },
        "l4": {
          "type": "ImplicitCurve",
          "expression": "x + y",
          "variables": [
            "x",
            "y"
          ]
        }
      },
      "styles": {
        "l1": {
          "color": "#ff7f0e"
        },
        "l2": {
          "color": "#1f77b4"
        },
        "l3": {
          "color": "#2ca02c"
        },
        "l4": {
          "color": "#d62728"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:01.799060",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_040",
    "name": "Polygon Hexagon",
    "description": "A regular-like convex hexagon constructed from polygonal edges.",
    "complexity_tier": 3,
    "tier_name": "Composite & Spiral Shapes",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 168.58,
    "scene_file": "scenes/scene_040.json",
    "image_file": "images/scene_040.png",
    "scene_data": {
      "objects": {
        "hex": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "0.8661855860486*x + 0.499722453489577*y - 1.2992783790729",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "xmin": 0.75,
              "xmax": 1.5,
              "ymin": 0.0,
              "ymax": 1.3,
              "endpoints": [
                [
                  1.5,
                  0.0
                ],
                [
                  0.75,
                  1.3
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.0*y - 1.3",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "xmin": -0.75,
              "xmax": 0.75,
              "ymin": 1.3,
              "ymax": 1.3,
              "endpoints": [
                [
                  0.75,
                  1.3
                ],
                [
                  -0.75,
                  1.3
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-0.8661855860486*x + 0.499722453489577*y - 1.2992783790729",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "xmin": -1.5,
              "xmax": -0.75,
              "ymin": 0.0,
              "ymax": 1.3,
              "endpoints": [
                [
                  -0.75,
                  1.3
                ],
                [
                  -1.5,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-0.8661855860486*x - 0.499722453489577*y - 1.2992783790729",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "xmin": -1.5,
              "xmax": -0.75,
              "ymin": -1.3,
              "ymax": 0.0,
              "endpoints": [
                [
                  -1.5,
                  0.0
                ],
                [
                  -0.75,
                  -1.3
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.0*y - 1.3",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "xmin": -0.75,
              "xmax": 0.75,
              "ymin": -1.3,
              "ymax": -1.3,
              "endpoints": [
                [
                  -0.75,
                  -1.3
                ],
                [
                  0.75,
                  -1.3
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "0.8661855860486*x - 0.499722453489577*y - 1.2992783790729",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "xmin": 0.75,
              "xmax": 1.5,
              "ymin": -1.3,
              "ymax": 0.0,
              "endpoints": [
                [
                  0.75,
                  -1.3
                ],
                [
                  1.5,
                  0.0
                ]
              ]
            }
          ],
          "segment_count": 6,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": true,
          "convex_edges_abc": [
            [
              0.8661855860486004,
              0.4997224534895771,
              -1.2992783790729006
            ],
            [
              0.0,
              1.0,
              -1.3
            ],
            [
              -0.8661855860486004,
              0.4997224534895771,
              -1.2992783790729006
            ],
            [
              -0.8661855860486004,
              -0.4997224534895771,
              -1.2992783790729006
            ],
            [
              0.0,
              -1.0,
              -1.3
            ],
            [
              0.8661855860486004,
              -0.4997224534895771,
              -1.2992783790729006
            ]
          ],
          "polygon_vertices": [
            [
              1.5,
              0.0
            ],
            [
              0.75,
              1.3
            ],
            [
              -0.75,
              1.3
            ],
            [
              -1.5,
              0.0
            ],
            [
              -0.75,
              -1.3
            ],
            [
              0.75,
              -1.3
            ]
          ]
        }
      },
      "styles": {
        "hex": {
          "color": "#17becf",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:01.935387",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_041",
    "name": "Circle Signed Distance Field",
    "description": "Signed distance field generated from a circular region.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 190.47,
    "scene_file": "scenes/scene_041.json",
    "image_file": "images/scene_041.png",
    "scene_data": {
      "objects": {
        "circle_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 4.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0,
                  0
                ],
                [
                  0,
                  2.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 4.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  2.0
                ],
                [
                  -2.0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 4.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0,
                  0
                ],
                [
                  0,
                  -2.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 4.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -2.0
                ],
                [
                  2.0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle_sdf": {
          "type": "SignedDistanceField",
          "region": {
            "type": "AreaRegion",
            "outer_boundary": {
              "type": "CompositeCurve",
              "segments": [
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 4.0",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      2.0,
                      0
                    ],
                    [
                      0,
                      2.0
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 4.0",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      0,
                      2.0
                    ],
                    [
                      -2.0,
                      0
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 4.0",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -2.0,
                      0
                    ],
                    [
                      0,
                      -2.0
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 4.0",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      0,
                      -2.0
                    ],
                    [
                      2.0,
                      0
                    ]
                  ]
                }
              ],
              "segment_count": 4,
              "variables": [
                "x",
                "y"
              ],
              "is_square": false,
              "square_bounds": null,
              "is_convex_polygon": false,
              "convex_edges_abc": null,
              "polygon_vertices": null
            },
            "holes": []
          },
          "resolution": 0.1
        }
      },
      "styles": {
        "circle_boundary": {
          "color": "#1f77b4",
          "linewidth": 1.5
        },
        "circle_sdf": {
          "color": "#1f77b4",
          "fill_alpha": 0.3
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:02.128296",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_042",
    "name": "Rectangle Signed Distance Field",
    "description": "Signed distance field generated from a rectangular region.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 136.92,
    "scene_file": "scenes/scene_042.json",
    "image_file": "images/scene_042.png",
    "scene_data": {
      "objects": {
        "rect_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2,
                  -1
                ],
                [
                  2,
                  -1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2,
                  -1
                ],
                [
                  2,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2,
                  1
                ],
                [
                  -2,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2,
                  1
                ],
                [
                  -2,
                  -1
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -2,
            2,
            -1,
            1
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "rect_sdf": {
          "type": "SignedDistanceField",
          "region": {
            "type": "AreaRegion",
            "outer_boundary": {
              "type": "CompositeCurve",
              "segments": [
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "y + 1",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -2,
                      -1
                    ],
                    [
                      2,
                      -1
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "x - 2",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      2,
                      -1
                    ],
                    [
                      2,
                      1
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "y - 1",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      2,
                      1
                    ],
                    [
                      -2,
                      1
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "x + 2",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -2,
                      1
                    ],
                    [
                      -2,
                      -1
                    ]
                  ]
                }
              ],
              "segment_count": 4,
              "variables": [
                "x",
                "y"
              ],
              "is_square": true,
              "square_bounds": [
                -2,
                2,
                -1,
                1
              ],
              "is_convex_polygon": false,
              "convex_edges_abc": null,
              "polygon_vertices": null
            },
            "holes": []
          },
          "resolution": 0.1
        }
      },
      "styles": {
        "rect_boundary": {
          "color": "#d62728",
          "linewidth": 1.5
        },
        "rect_sdf": {
          "color": "#d62728",
          "fill_alpha": 0.35,
          "fill_color": "salmon"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:02.338745",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_043",
    "name": "Triangle Signed Distance Field",
    "description": "Signed distance field generated from a triangular region.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 160.84,
    "scene_file": "scenes/scene_043.json",
    "image_file": "images/scene_043.png",
    "scene_data": {
      "objects": {
        "tri_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -0.5
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  -1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "tri_sdf": {
          "type": "SignedDistanceField",
          "region": {
            "type": "AreaRegion",
            "outer_boundary": {
              "type": "CompositeCurve",
              "segments": [
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "y + 0.5",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -1,
                      -0.5
                    ],
                    [
                      1,
                      -0.5
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "1.5*x + y - 1",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      1,
                      -0.5
                    ],
                    [
                      0,
                      1
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "-1.5*x + y - 1",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      0,
                      1
                    ],
                    [
                      -1,
                      -0.5
                    ]
                  ]
                }
              ],
              "segment_count": 3,
              "variables": [
                "x",
                "y"
              ],
              "is_square": false,
              "square_bounds": null,
              "is_convex_polygon": false,
              "convex_edges_abc": null,
              "polygon_vertices": null
            },
            "holes": []
          },
          "resolution": 0.1
        }
      },
      "styles": {
        "tri_boundary": {
          "color": "#2ca02c",
          "linewidth": 1.5
        },
        "tri_sdf": {
          "color": "#2ca02c",
          "fill_alpha": 0.3,
          "fill_color": "lightgreen"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:02.500248",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_044",
    "name": "Circle Occupancy Field",
    "description": "Binary occupancy field generated from a circular region.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 170.25,
    "scene_file": "scenes/scene_044.json",
    "image_file": "images/scene_044.png",
    "scene_data": {
      "objects": {
        "circle_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  0
                ],
                [
                  0,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1.5
                ],
                [
                  -1.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  0
                ],
                [
                  0,
                  -1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -1.5
                ],
                [
                  1.5,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle_occ": {
          "type": "OccupancyField",
          "region": {
            "type": "AreaRegion",
            "outer_boundary": {
              "type": "CompositeCurve",
              "segments": [
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 2.25",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      1.5,
                      0
                    ],
                    [
                      0,
                      1.5
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 2.25",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      0,
                      1.5
                    ],
                    [
                      -1.5,
                      0
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 2.25",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -1.5,
                      0
                    ],
                    [
                      0,
                      -1.5
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 2.25",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      0,
                      -1.5
                    ],
                    [
                      1.5,
                      0
                    ]
                  ]
                }
              ],
              "segment_count": 4,
              "variables": [
                "x",
                "y"
              ],
              "is_square": false,
              "square_bounds": null,
              "is_convex_polygon": false,
              "convex_edges_abc": null,
              "polygon_vertices": null
            },
            "holes": []
          },
          "inside_value": 1.0,
          "outside_value": 0.0
        }
      },
      "styles": {
        "circle_boundary": {
          "color": "#1f77b4",
          "linewidth": 1.5,
          "linestyle": "dashed"
        },
        "circle_occ": {
          "color": "#1f77b4",
          "fill_color": "skyblue",
          "fill_alpha": 0.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:02.687629",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_045",
    "name": "Square Occupancy Field",
    "description": "Binary occupancy field generated from a square region.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 121.58,
    "scene_file": "scenes/scene_045.json",
    "image_file": "images/scene_045.png",
    "scene_data": {
      "objects": {
        "square_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.2,
                  -1.2
                ],
                [
                  1.2,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1.2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.2,
                  -1.2
                ],
                [
                  1.2,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1.2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.2,
                  1.2
                ],
                [
                  -1.2,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.2",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.2,
                  1.2
                ],
                [
                  -1.2,
                  -1.2
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.2,
            1.2,
            -1.2,
            1.2
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "square_occ": {
          "type": "OccupancyField",
          "region": {
            "type": "AreaRegion",
            "outer_boundary": {
              "type": "CompositeCurve",
              "segments": [
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "y + 1.2",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -1.2,
                      -1.2
                    ],
                    [
                      1.2,
                      -1.2
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "x - 1.2",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      1.2,
                      -1.2
                    ],
                    [
                      1.2,
                      1.2
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "y - 1.2",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      1.2,
                      1.2
                    ],
                    [
                      -1.2,
                      1.2
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "x + 1.2",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -1.2,
                      1.2
                    ],
                    [
                      -1.2,
                      -1.2
                    ]
                  ]
                }
              ],
              "segment_count": 4,
              "variables": [
                "x",
                "y"
              ],
              "is_square": true,
              "square_bounds": [
                -1.2,
                1.2,
                -1.2,
                1.2
              ],
              "is_convex_polygon": false,
              "convex_edges_abc": null,
              "polygon_vertices": null
            },
            "holes": []
          },
          "inside_value": 1.0,
          "outside_value": 0.0
        }
      },
      "styles": {
        "square_boundary": {
          "color": "#e377c2",
          "linewidth": 1.5,
          "linestyle": "dashed"
        },
        "square_occ": {
          "color": "#e377c2",
          "fill_color": "plum",
          "fill_alpha": 0.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:02.883031",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_046",
    "name": "Triangle Occupancy Field",
    "description": "Binary occupancy field generated from a triangular region.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 145.95,
    "scene_file": "scenes/scene_046.json",
    "image_file": "images/scene_046.png",
    "scene_data": {
      "objects": {
        "tri_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -0.5
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  -1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "tri_occ": {
          "type": "OccupancyField",
          "region": {
            "type": "AreaRegion",
            "outer_boundary": {
              "type": "CompositeCurve",
              "segments": [
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "y + 0.5",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -1,
                      -0.5
                    ],
                    [
                      1,
                      -0.5
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "1.5*x + y - 1",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      1,
                      -0.5
                    ],
                    [
                      0,
                      1
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "-1.5*x + y - 1",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      0,
                      1
                    ],
                    [
                      -1,
                      -0.5
                    ]
                  ]
                }
              ],
              "segment_count": 3,
              "variables": [
                "x",
                "y"
              ],
              "is_square": false,
              "square_bounds": null,
              "is_convex_polygon": false,
              "convex_edges_abc": null,
              "polygon_vertices": null
            },
            "holes": []
          },
          "inside_value": 1.0,
          "outside_value": 0.0
        }
      },
      "styles": {
        "tri_boundary": {
          "color": "#2ca02c",
          "linewidth": 1.5,
          "linestyle": "dashed"
        },
        "tri_occ": {
          "color": "#2ca02c",
          "fill_color": "lightgreen",
          "fill_alpha": 0.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:03.016632",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_047",
    "name": "Circle Curve Field",
    "description": "Scalar field wrapping a standard circle's implicit equation.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 126.28,
    "scene_file": "scenes/scene_047.json",
    "image_file": "images/scene_047.png",
    "scene_data": {
      "objects": {
        "circle_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  0
                ],
                [
                  0,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1.5
                ],
                [
                  -1.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  0
                ],
                [
                  0,
                  -1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -1.5
                ],
                [
                  1.5,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle_cf": {
          "type": "CurveField",
          "curve": {
            "type": "ConicSection",
            "expression": "x**2 + y**2 - 2.25",
            "variables": [
              "x",
              "y"
            ],
            "conic_type": "circle"
          }
        }
      },
      "styles": {
        "circle_boundary": {
          "color": "#1f77b4",
          "linewidth": 1.5
        },
        "circle_cf": {
          "color": "#1f77b4"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:03.185746",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_048",
    "name": "Ellipse Curve Field",
    "description": "Scalar field wrapping an ellipse's implicit equation.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 91.16,
    "scene_file": "scenes/scene_048.json",
    "image_file": "images/scene_048.png",
    "scene_data": {
      "objects": {
        "ellipse_boundary": {
          "type": "TrimmedImplicitCurve",
          "base_curve": {
            "type": "ConicSection",
            "expression": "0.16*x**2 + 0.64*y**2 - 1",
            "variables": [
              "x",
              "y"
            ],
            "conic_type": "ellipse"
          },
          "variables": [
            "x",
            "y"
          ],
          "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
          "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
        },
        "ellipse_cf": {
          "type": "CurveField",
          "curve": {
            "type": "ConicSection",
            "expression": "0.16*x**2 + 0.64*y**2 - 1",
            "variables": [
              "x",
              "y"
            ],
            "conic_type": "ellipse"
          }
        }
      },
      "styles": {
        "ellipse_boundary": {
          "color": "#9467bd",
          "linewidth": 1.5
        },
        "ellipse_cf": {
          "color": "#9467bd"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:03.330040",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_049",
    "name": "Parabola Curve Field",
    "description": "Scalar field wrapping an upward parabola.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 77.11,
    "scene_file": "scenes/scene_049.json",
    "image_file": "images/scene_049.png",
    "scene_data": {
      "objects": {
        "parabola_boundary": {
          "type": "TrimmedImplicitCurve",
          "base_curve": {
            "type": "ImplicitCurve",
            "expression": "-0.5*x**2 + y",
            "variables": [
              "x",
              "y"
            ]
          },
          "variables": [
            "x",
            "y"
          ],
          "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
          "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
        },
        "parabola_cf": {
          "type": "CurveField",
          "curve": {
            "type": "ImplicitCurve",
            "expression": "-0.5*x**2 + y",
            "variables": [
              "x",
              "y"
            ]
          }
        }
      },
      "styles": {
        "parabola_boundary": {
          "color": "#ff7f0e",
          "linewidth": 1.5
        },
        "parabola_cf": {
          "color": "#ff7f0e"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:03.441205",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_050",
    "name": "Line Curve Field",
    "description": "Scalar field wrapping a diagonal line.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 1,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 79.81,
    "scene_file": "scenes/scene_050.json",
    "image_file": "images/scene_050.png",
    "scene_data": {
      "objects": {
        "line_boundary": {
          "type": "TrimmedImplicitCurve",
          "base_curve": {
            "type": "ImplicitCurve",
            "expression": "x - y",
            "variables": [
              "x",
              "y"
            ]
          },
          "variables": [
            "x",
            "y"
          ],
          "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
          "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
        },
        "line_cf": {
          "type": "CurveField",
          "curve": {
            "type": "ImplicitCurve",
            "expression": "x - y",
            "variables": [
              "x",
              "y"
            ]
          }
        }
      },
      "styles": {
        "line_boundary": {
          "color": "#2ca02c",
          "linewidth": 1.5
        },
        "line_cf": {
          "color": "#2ca02c"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:03.532957",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_051",
    "name": "Blended Field: Circle + Ellipse (Add)",
    "description": "Addition blend of a circular curve field and an elliptical curve field.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 152.12,
    "scene_file": "scenes/scene_051.json",
    "image_file": "images/scene_051.png",
    "scene_data": {
      "objects": {
        "circle_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 1.0)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.19999999999999996,
                  0
                ],
                [
                  -1.0,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 1.0)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.0,
                  1.2
                ],
                [
                  -2.2,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 1.0)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.2,
                  0
                ],
                [
                  -1.0,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 1.0)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.0,
                  -1.2
                ],
                [
                  0.19999999999999996,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "ellipse_boundary": {
          "type": "TrimmedImplicitCurve",
          "base_curve": {
            "type": "ConicSection",
            "expression": "1.0*y**2 + 0.444444444444444*(x - 1.0)**2 - 1",
            "variables": [
              "x",
              "y"
            ],
            "conic_type": "ellipse"
          },
          "variables": [
            "x",
            "y"
          ],
          "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
          "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
        },
        "blend_add": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 1.0)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "1.0*y**2 + 0.444444444444444*(x - 1.0)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              }
            }
          ],
          "operation": "add"
        }
      },
      "styles": {
        "circle_boundary": {
          "color": "#1f77b4",
          "linewidth": 1.5
        },
        "ellipse_boundary": {
          "color": "#1f77b4",
          "linewidth": 1.5
        },
        "blend_add": {
          "color": "#1f77b4"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:03.630863",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_052",
    "name": "Blended Field: Ellipse - Circle (Subtract)",
    "description": "Subtraction blend of a circular curve field from an ellipse field.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 144.48,
    "scene_file": "scenes/scene_052.json",
    "image_file": "images/scene_052.png",
    "scene_data": {
      "objects": {
        "ellipse_boundary": {
          "type": "TrimmedImplicitCurve",
          "base_curve": {
            "type": "ConicSection",
            "expression": "0.16*x**2 + 0.444444444444444*y**2 - 1",
            "variables": [
              "x",
              "y"
            ],
            "conic_type": "ellipse"
          },
          "variables": [
            "x",
            "y"
          ],
          "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
          "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
        },
        "circle_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0
                ],
                [
                  0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1.0
                ],
                [
                  -1.0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.0,
                  0
                ],
                [
                  0,
                  -1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -1.0
                ],
                [
                  1.0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_sub": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "0.16*x**2 + 0.444444444444444*y**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            }
          ],
          "operation": "subtract"
        }
      },
      "styles": {
        "ellipse_boundary": {
          "color": "#9467bd",
          "linewidth": 1.5
        },
        "circle_boundary": {
          "color": "#9467bd",
          "linewidth": 1.5
        },
        "blend_sub": {
          "color": "#9467bd"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:03.812300",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_053",
    "name": "Blended Field: Two Circles (Multiply)",
    "description": "Multiplicative blend of two circular curve fields.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 202.26,
    "scene_file": "scenes/scene_053.json",
    "image_file": "images/scene_053.png",
    "scene_data": {
      "objects": {
        "circle1_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.3999999999999999,
                  0
                ],
                [
                  -0.8,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8,
                  1.2
                ],
                [
                  -2.0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0,
                  0
                ],
                [
                  -0.8,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8,
                  -1.2
                ],
                [
                  0.3999999999999999,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle2_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0,
                  0
                ],
                [
                  0.8,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8,
                  1.2
                ],
                [
                  -0.3999999999999999,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3999999999999999,
                  0
                ],
                [
                  0.8,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8,
                  -1.2
                ],
                [
                  2.0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_mul": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            }
          ],
          "operation": "multiply"
        }
      },
      "styles": {
        "circle1_boundary": {
          "color": "#ff7f0e",
          "linewidth": 1.5
        },
        "circle2_boundary": {
          "color": "#ff7f0e",
          "linewidth": 1.5
        },
        "blend_mul": {
          "color": "#ff7f0e"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:03.974161",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_054",
    "name": "Blended Field: Two Circles (Min/Union)",
    "description": "Minimum blend of two circular fields, representing shape union.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 234.57,
    "scene_file": "scenes/scene_054.json",
    "image_file": "images/scene_054.png",
    "scene_data": {
      "objects": {
        "circle1_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.3999999999999999,
                  0
                ],
                [
                  -0.8,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8,
                  1.2
                ],
                [
                  -2.0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0,
                  0
                ],
                [
                  -0.8,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8,
                  -1.2
                ],
                [
                  0.3999999999999999,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle2_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0,
                  0
                ],
                [
                  0.8,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8,
                  1.2
                ],
                [
                  -0.3999999999999999,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3999999999999999,
                  0
                ],
                [
                  0.8,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8,
                  -1.2
                ],
                [
                  2.0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_min": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "circle1_boundary": {
          "color": "#d62728",
          "linewidth": 1.5
        },
        "circle2_boundary": {
          "color": "#d62728",
          "linewidth": 1.5
        },
        "blend_min": {
          "color": "#d62728"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:04.198758",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_055",
    "name": "Blended Field: Two Circles (Max/Intersection)",
    "description": "Maximum blend of two circular fields, representing shape intersection.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 205.89,
    "scene_file": "scenes/scene_055.json",
    "image_file": "images/scene_055.png",
    "scene_data": {
      "objects": {
        "circle1_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.3999999999999999,
                  0
                ],
                [
                  -0.8,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8,
                  1.2
                ],
                [
                  -2.0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0,
                  0
                ],
                [
                  -0.8,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8,
                  -1.2
                ],
                [
                  0.3999999999999999,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle2_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0,
                  0
                ],
                [
                  0.8,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8,
                  1.2
                ],
                [
                  -0.3999999999999999,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3999999999999999,
                  0
                ],
                [
                  0.8,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8,
                  -1.2
                ],
                [
                  2.0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_max": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            }
          ],
          "operation": "max"
        }
      },
      "styles": {
        "circle1_boundary": {
          "color": "#2ca02c",
          "linewidth": 1.5
        },
        "circle2_boundary": {
          "color": "#2ca02c",
          "linewidth": 1.5
        },
        "blend_max": {
          "color": "#2ca02c"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:04.456181",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_056",
    "name": "Blended Field: Two Circles (Average)",
    "description": "Average blend of two circular fields.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 208.34,
    "scene_file": "scenes/scene_056.json",
    "image_file": "images/scene_056.png",
    "scene_data": {
      "objects": {
        "circle1_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.3999999999999999,
                  0
                ],
                [
                  -0.8,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8,
                  1.2
                ],
                [
                  -2.0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0,
                  0
                ],
                [
                  -0.8,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8,
                  -1.2
                ],
                [
                  0.3999999999999999,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle2_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0,
                  0
                ],
                [
                  0.8,
                  1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8,
                  1.2
                ],
                [
                  -0.3999999999999999,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3999999999999999,
                  0
                ],
                [
                  0.8,
                  -1.2
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8,
                  -1.2
                ],
                [
                  2.0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_avg": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            }
          ],
          "operation": "average"
        }
      },
      "styles": {
        "circle1_boundary": {
          "color": "#e377c2",
          "linewidth": 1.5
        },
        "circle2_boundary": {
          "color": "#e377c2",
          "linewidth": 1.5
        },
        "blend_avg": {
          "color": "#e377c2"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:04.684372",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_057",
    "name": "Blended SDF: Square + Circle (Min)",
    "description": "Minimum blend of a square distance field and a circular distance field.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 279.96,
    "scene_file": "scenes/scene_057.json",
    "image_file": "images/scene_057.png",
    "scene_data": {
      "objects": {
        "square_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  -1.5
                ],
                [
                  0.5,
                  -1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  -1.5
                ],
                [
                  0.5,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  0.5
                ],
                [
                  -1.5,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  0.5
                ],
                [
                  -1.5,
                  -1.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.5,
            0.5,
            -1.5,
            0.5
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.75,
                  0.5
                ],
                [
                  0.5,
                  1.75
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  1.75
                ],
                [
                  -0.75,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.75,
                  0.5
                ],
                [
                  0.5,
                  -0.75
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  -0.75
                ],
                [
                  1.75,
                  0.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_sdf_min": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "SignedDistanceField",
              "region": {
                "type": "AreaRegion",
                "outer_boundary": {
                  "type": "CompositeCurve",
                  "segments": [
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "PolynomialCurve",
                        "expression": "y + 1.5",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "degree": 1
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -1.5,
                          -1.5
                        ],
                        [
                          0.5,
                          -1.5
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "PolynomialCurve",
                        "expression": "x - 0.5",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "degree": 1
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          -1.5
                        ],
                        [
                          0.5,
                          0.5
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "PolynomialCurve",
                        "expression": "y - 0.5",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "degree": 1
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          0.5
                        ],
                        [
                          -1.5,
                          0.5
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "PolynomialCurve",
                        "expression": "x + 1.5",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "degree": 1
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -1.5,
                          0.5
                        ],
                        [
                          -1.5,
                          -1.5
                        ]
                      ]
                    }
                  ],
                  "segment_count": 4,
                  "variables": [
                    "x",
                    "y"
                  ],
                  "is_square": true,
                  "square_bounds": [
                    -1.5,
                    0.5,
                    -1.5,
                    0.5
                  ],
                  "is_convex_polygon": false,
                  "convex_edges_abc": null,
                  "polygon_vertices": null
                },
                "holes": []
              },
              "resolution": 0.1
            },
            {
              "type": "SignedDistanceField",
              "region": {
                "type": "AreaRegion",
                "outer_boundary": {
                  "type": "CompositeCurve",
                  "segments": [
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          1.75,
                          0.5
                        ],
                        [
                          0.5,
                          1.75
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          1.75
                        ],
                        [
                          -0.75,
                          0.5
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -0.75,
                          0.5
                        ],
                        [
                          0.5,
                          -0.75
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          -0.75
                        ],
                        [
                          1.75,
                          0.5
                        ]
                      ]
                    }
                  ],
                  "segment_count": 4,
                  "variables": [
                    "x",
                    "y"
                  ],
                  "is_square": false,
                  "square_bounds": null,
                  "is_convex_polygon": false,
                  "convex_edges_abc": null,
                  "polygon_vertices": null
                },
                "holes": []
              },
              "resolution": 0.1
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "square_boundary": {
          "color": "#17becf",
          "linewidth": 1.5
        },
        "circle_boundary": {
          "color": "#17becf",
          "linewidth": 1.5
        },
        "blend_sdf_min": {
          "color": "#17becf",
          "fill_alpha": 0.3
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:04.919031",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_058",
    "name": "Blended SDF: Square & Circle (Max)",
    "description": "Maximum blend of a square distance field and a circular distance field.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 265.93,
    "scene_file": "scenes/scene_058.json",
    "image_file": "images/scene_058.png",
    "scene_data": {
      "objects": {
        "square_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  -1.5
                ],
                [
                  0.5,
                  -1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  -1.5
                ],
                [
                  0.5,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  0.5
                ],
                [
                  -1.5,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  0.5
                ],
                [
                  -1.5,
                  -1.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.5,
            0.5,
            -1.5,
            0.5
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.75,
                  0.5
                ],
                [
                  0.5,
                  1.75
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  1.75
                ],
                [
                  -0.75,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.75,
                  0.5
                ],
                [
                  0.5,
                  -0.75
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  -0.75
                ],
                [
                  1.75,
                  0.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_sdf_max": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "SignedDistanceField",
              "region": {
                "type": "AreaRegion",
                "outer_boundary": {
                  "type": "CompositeCurve",
                  "segments": [
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "PolynomialCurve",
                        "expression": "y + 1.5",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "degree": 1
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -1.5,
                          -1.5
                        ],
                        [
                          0.5,
                          -1.5
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "PolynomialCurve",
                        "expression": "x - 0.5",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "degree": 1
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          -1.5
                        ],
                        [
                          0.5,
                          0.5
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "PolynomialCurve",
                        "expression": "y - 0.5",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "degree": 1
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          0.5
                        ],
                        [
                          -1.5,
                          0.5
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "PolynomialCurve",
                        "expression": "x + 1.5",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "degree": 1
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -1.5,
                          0.5
                        ],
                        [
                          -1.5,
                          -1.5
                        ]
                      ]
                    }
                  ],
                  "segment_count": 4,
                  "variables": [
                    "x",
                    "y"
                  ],
                  "is_square": true,
                  "square_bounds": [
                    -1.5,
                    0.5,
                    -1.5,
                    0.5
                  ],
                  "is_convex_polygon": false,
                  "convex_edges_abc": null,
                  "polygon_vertices": null
                },
                "holes": []
              },
              "resolution": 0.1
            },
            {
              "type": "SignedDistanceField",
              "region": {
                "type": "AreaRegion",
                "outer_boundary": {
                  "type": "CompositeCurve",
                  "segments": [
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          1.75,
                          0.5
                        ],
                        [
                          0.5,
                          1.75
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          1.75
                        ],
                        [
                          -0.75,
                          0.5
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -0.75,
                          0.5
                        ],
                        [
                          0.5,
                          -0.75
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "(x - 0.5)**2 + (y - 0.5)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          -0.75
                        ],
                        [
                          1.75,
                          0.5
                        ]
                      ]
                    }
                  ],
                  "segment_count": 4,
                  "variables": [
                    "x",
                    "y"
                  ],
                  "is_square": false,
                  "square_bounds": null,
                  "is_convex_polygon": false,
                  "convex_edges_abc": null,
                  "polygon_vertices": null
                },
                "holes": []
              },
              "resolution": 0.1
            }
          ],
          "operation": "max"
        }
      },
      "styles": {
        "square_boundary": {
          "color": "#bcbd22",
          "linewidth": 1.5
        },
        "circle_boundary": {
          "color": "#bcbd22",
          "linewidth": 1.5
        },
        "blend_sdf_max": {
          "color": "#bcbd22",
          "fill_alpha": 0.3,
          "fill_color": "yellow"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:05.221846",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_059",
    "name": "Blended Occupancy: Two Circles (Max)",
    "description": "Maximum blend of two occupancy fields, representing binary union.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 300.41,
    "scene_file": "scenes/scene_059.json",
    "image_file": "images/scene_059.png",
    "scene_data": {
      "objects": {
        "circle1_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  0
                ],
                [
                  -0.75,
                  1.25
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.75,
                  1.25
                ],
                [
                  -2.0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0,
                  0
                ],
                [
                  -0.75,
                  -1.25
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.75,
                  -1.25
                ],
                [
                  0.5,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle2_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0,
                  0
                ],
                [
                  0.75,
                  1.25
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.75,
                  1.25
                ],
                [
                  -0.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  0
                ],
                [
                  0.75,
                  -1.25
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.75,
                  -1.25
                ],
                [
                  2.0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_occ_max": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "OccupancyField",
              "region": {
                "type": "AreaRegion",
                "outer_boundary": {
                  "type": "CompositeCurve",
                  "segments": [
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          0
                        ],
                        [
                          -0.75,
                          1.25
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -0.75,
                          1.25
                        ],
                        [
                          -2.0,
                          0
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -2.0,
                          0
                        ],
                        [
                          -0.75,
                          -1.25
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -0.75,
                          -1.25
                        ],
                        [
                          0.5,
                          0
                        ]
                      ]
                    }
                  ],
                  "segment_count": 4,
                  "variables": [
                    "x",
                    "y"
                  ],
                  "is_square": false,
                  "square_bounds": null,
                  "is_convex_polygon": false,
                  "convex_edges_abc": null,
                  "polygon_vertices": null
                },
                "holes": []
              },
              "inside_value": 1.0,
              "outside_value": 0.0
            },
            {
              "type": "OccupancyField",
              "region": {
                "type": "AreaRegion",
                "outer_boundary": {
                  "type": "CompositeCurve",
                  "segments": [
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          2.0,
                          0
                        ],
                        [
                          0.75,
                          1.25
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.75,
                          1.25
                        ],
                        [
                          -0.5,
                          0
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -0.5,
                          0
                        ],
                        [
                          0.75,
                          -1.25
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.75,
                          -1.25
                        ],
                        [
                          2.0,
                          0
                        ]
                      ]
                    }
                  ],
                  "segment_count": 4,
                  "variables": [
                    "x",
                    "y"
                  ],
                  "is_square": false,
                  "square_bounds": null,
                  "is_convex_polygon": false,
                  "convex_edges_abc": null,
                  "polygon_vertices": null
                },
                "holes": []
              },
              "inside_value": 1.0,
              "outside_value": 0.0
            }
          ],
          "operation": "max"
        }
      },
      "styles": {
        "circle1_boundary": {
          "color": "#1f77b4",
          "linewidth": 1.5,
          "linestyle": "dashed"
        },
        "circle2_boundary": {
          "color": "#1f77b4",
          "linewidth": 1.5,
          "linestyle": "dashed"
        },
        "blend_occ_max": {
          "color": "#1f77b4",
          "fill_color": "skyblue",
          "fill_alpha": 0.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:05.512471",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_060",
    "name": "Blended Occupancy: Two Circles (Min)",
    "description": "Minimum blend of two occupancy fields, representing binary intersection.",
    "complexity_tier": 4,
    "tier_name": "Scalar Fields & Containment",
    "curves_count": 2,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 303.0,
    "scene_file": "scenes/scene_060.json",
    "image_file": "images/scene_060.png",
    "scene_data": {
      "objects": {
        "circle1_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5,
                  0
                ],
                [
                  -0.75,
                  1.25
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.75,
                  1.25
                ],
                [
                  -2.0,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0,
                  0
                ],
                [
                  -0.75,
                  -1.25
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.75,
                  -1.25
                ],
                [
                  0.5,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "circle2_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0,
                  0
                ],
                [
                  0.75,
                  1.25
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.75,
                  1.25
                ],
                [
                  -0.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  0
                ],
                [
                  0.75,
                  -1.25
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.75,
                  -1.25
                ],
                [
                  2.0,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "blend_occ_min": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "OccupancyField",
              "region": {
                "type": "AreaRegion",
                "outer_boundary": {
                  "type": "CompositeCurve",
                  "segments": [
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.5,
                          0
                        ],
                        [
                          -0.75,
                          1.25
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -0.75,
                          1.25
                        ],
                        [
                          -2.0,
                          0
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -2.0,
                          0
                        ],
                        [
                          -0.75,
                          -1.25
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x + 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -0.75,
                          -1.25
                        ],
                        [
                          0.5,
                          0
                        ]
                      ]
                    }
                  ],
                  "segment_count": 4,
                  "variables": [
                    "x",
                    "y"
                  ],
                  "is_square": false,
                  "square_bounds": null,
                  "is_convex_polygon": false,
                  "convex_edges_abc": null,
                  "polygon_vertices": null
                },
                "holes": []
              },
              "inside_value": 1.0,
              "outside_value": 0.0
            },
            {
              "type": "OccupancyField",
              "region": {
                "type": "AreaRegion",
                "outer_boundary": {
                  "type": "CompositeCurve",
                  "segments": [
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          2.0,
                          0
                        ],
                        [
                          0.75,
                          1.25
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.75,
                          1.25
                        ],
                        [
                          -0.5,
                          0
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          -0.5,
                          0
                        ],
                        [
                          0.75,
                          -1.25
                        ]
                      ]
                    },
                    {
                      "type": "TrimmedImplicitCurve",
                      "base_curve": {
                        "type": "ConicSection",
                        "expression": "y**2 + (x - 0.75)**2 - 1.5625",
                        "variables": [
                          "x",
                          "y"
                        ],
                        "conic_type": "circle"
                      },
                      "variables": [
                        "x",
                        "y"
                      ],
                      "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                      "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                      "endpoints": [
                        [
                          0.75,
                          -1.25
                        ],
                        [
                          2.0,
                          0
                        ]
                      ]
                    }
                  ],
                  "segment_count": 4,
                  "variables": [
                    "x",
                    "y"
                  ],
                  "is_square": false,
                  "square_bounds": null,
                  "is_convex_polygon": false,
                  "convex_edges_abc": null,
                  "polygon_vertices": null
                },
                "holes": []
              },
              "inside_value": 1.0,
              "outside_value": 0.0
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "circle1_boundary": {
          "color": "#2ca02c",
          "linewidth": 1.5,
          "linestyle": "dashed"
        },
        "circle2_boundary": {
          "color": "#2ca02c",
          "linewidth": 1.5,
          "linestyle": "dashed"
        },
        "blend_occ_min": {
          "color": "#2ca02c",
          "fill_color": "lightgreen",
          "fill_alpha": 0.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:05.837240",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_061",
    "name": "Circle Dependency Chain (2 Levels)",
    "description": "Circle 2 depends on Circle 1's radius; Circle 3 depends on Circle 2.",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 3,
    "fields_count": 0,
    "dependency_depth": 2,
    "total_time_ms": 123.05,
    "scene_file": "scenes/scene_061.json",
    "image_file": "images/scene_061.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 2.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c3": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 2.0)**2 - 0.0625",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "c3": {
          "color": "#ff7f0e"
        }
      },
      "groups": {},
      "dependencies": {
        "c1": [
          "c2"
        ],
        "c2": [
          "c3"
        ]
      },
      "reverse_dependencies": {
        "c2": [
          "c1"
        ],
        "c3": [
          "c2"
        ]
      },
      "dependency_descriptions": {
        "c2": {
          "c1": "Radius binds to c1.radius * 0.5; offset along x-axis"
        },
        "c3": {
          "c2": "Radius binds to c2.radius * 0.5; offset along negative x-axis"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:46.110032",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_062",
    "name": "Deep Circle Dependency Chain (4 Levels)",
    "description": "A 4-tier deep chain of geometric object dependencies.",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 4,
    "fields_count": 0,
    "dependency_depth": 3,
    "total_time_ms": 126.64,
    "scene_file": "scenes/scene_062.json",
    "image_file": "images/scene_062.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 0.5625",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c3": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 2.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c4": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 3.2)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "c3": {
          "color": "#ff7f0e"
        },
        "c4": {
          "color": "#d62728"
        }
      },
      "groups": {},
      "dependencies": {
        "c1": [
          "c2"
        ],
        "c2": [
          "c3"
        ],
        "c3": [
          "c4"
        ]
      },
      "reverse_dependencies": {
        "c2": [
          "c1"
        ],
        "c3": [
          "c2"
        ],
        "c4": [
          "c3"
        ]
      },
      "dependency_descriptions": {
        "c2": {
          "c1": "Radius scales to 0.75x parent radius"
        },
        "c3": {
          "c2": "Radius scales to 0.67x parent radius"
        },
        "c4": {
          "c3": "Radius scales to 0.6x parent radius"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:46.250162",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_063",
    "name": "Branching Dependency Tree",
    "description": "Branching dependency tree with one root and three dependents.",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 4,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 113.18,
    "scene_file": "scenes/scene_063.json",
    "image_file": "images/scene_063.png",
    "scene_data": {
      "objects": {
        "root": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 2.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep1": {
          "type": "ConicSection",
          "expression": "(x + 2.0)**2 + (y - 2.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep2": {
          "type": "ConicSection",
          "expression": "(x - 2.0)**2 + (y - 2.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep3": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 2.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "root": {
          "color": "#1f77b4",
          "linewidth": 3
        },
        "dep1": {
          "color": "#2ca02c"
        },
        "dep2": {
          "color": "#ff7f0e"
        },
        "dep3": {
          "color": "#d62728"
        }
      },
      "groups": {},
      "dependencies": {
        "root": [
          "dep1",
          "dep2",
          "dep3"
        ]
      },
      "reverse_dependencies": {
        "dep1": [
          "root"
        ],
        "dep2": [
          "root"
        ],
        "dep3": [
          "root"
        ]
      },
      "dependency_descriptions": {
        "dep1": {
          "root": "Center anchored at root.center + (-2.0, 2.0)"
        },
        "dep2": {
          "root": "Center anchored at root.center + (2.0, 2.0)"
        },
        "dep3": {
          "root": "Center anchored at root.center + (0.0, -2.0)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:46.388376",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_064",
    "name": "Converging Dependency Tree",
    "description": "Multiple independent source shapes converging onto a single dependent composite shape.",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 3,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 86.4,
    "scene_file": "scenes/scene_064.json",
    "image_file": "images/scene_064.png",
    "scene_data": {
      "objects": {
        "src1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 2.0)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "src2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 2.0)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dependent": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 2.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "src1": {
          "color": "#1f77b4"
        },
        "src2": {
          "color": "#2ca02c"
        },
        "dependent": {
          "color": "#ff7f0e",
          "linewidth": 3
        }
      },
      "groups": {},
      "dependencies": {
        "src1": [
          "dependent"
        ],
        "src2": [
          "dependent"
        ]
      },
      "reverse_dependencies": {
        "dependent": [
          "src1",
          "src2"
        ]
      },
      "dependency_descriptions": {
        "dependent": {
          "src1": "Center anchored midway between src1 and src2 centers",
          "src2": "Center anchored midway between src1 and src2 centers"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:46.515148",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_065",
    "name": "Composite Curve with Dependencies",
    "description": "A composite D-shape where the straight segment depends on the circular outer boundary.",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 134.11,
    "scene_file": "scenes/scene_065.json",
    "image_file": "images/scene_065.png",
    "scene_data": {
      "objects": {
        "boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  0
                ],
                [
                  0,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1.5
                ],
                [
                  -1.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  0
                ],
                [
                  0,
                  -1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -1.5
                ],
                [
                  1.5,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "divider": {
          "type": "ImplicitCurve",
          "expression": "x",
          "variables": [
            "x",
            "y"
          ]
        }
      },
      "styles": {
        "boundary": {
          "color": "#1f77b4"
        },
        "divider": {
          "color": "#d62728"
        }
      },
      "groups": {},
      "dependencies": {
        "boundary": [
          "divider"
        ]
      },
      "reverse_dependencies": {
        "divider": [
          "boundary"
        ]
      },
      "dependency_descriptions": {
        "divider": {
          "boundary": "Divider endpoints snap to boundary intersection points"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:46.612260",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_066",
    "name": "Blended Field Dependency Tree",
    "description": "A blended field depending explicitly on its child curve fields.",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 0,
    "fields_count": 3,
    "dependency_depth": 1,
    "total_time_ms": 74.68,
    "scene_file": "scenes/scene_066.json",
    "image_file": "images/scene_066.png",
    "scene_data": {
      "objects": {
        "cf1": {
          "type": "CurveField",
          "curve": {
            "type": "ConicSection",
            "expression": "(x + 1.0)**2 + (y + 1.0)**2 - 1.44",
            "variables": [
              "x",
              "y"
            ],
            "conic_type": "circle"
          }
        },
        "cf2": {
          "type": "CurveField",
          "curve": {
            "type": "ConicSection",
            "expression": "(x - 1.0)**2 + (y - 1.0)**2 - 1.44",
            "variables": [
              "x",
              "y"
            ],
            "conic_type": "circle"
          }
        },
        "blend": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x + 1.0)**2 + (y + 1.0)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x - 1.0)**2 + (y - 1.0)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "cf1": {
          "color": "#aec7e8"
        },
        "cf2": {
          "color": "#ffbb78"
        },
        "blend": {
          "color": "#d62728",
          "linewidth": 3
        }
      },
      "groups": {},
      "dependencies": {
        "cf1": [
          "blend"
        ],
        "cf2": [
          "blend"
        ]
      },
      "reverse_dependencies": {
        "blend": [
          "cf1",
          "cf2"
        ]
      },
      "dependency_descriptions": {
        "blend": {
          "cf1": "Evaluates min(cf1, cf2) to construct the union blended region",
          "cf2": "Evaluates min(cf1, cf2) to construct the union blended region"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:46.760802",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_067",
    "name": "Hierarchical Blend Scene 1",
    "description": "Complex blended scalar field combining multiple curve types (Idx: 67).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 3,
    "fields_count": 1,
    "dependency_depth": 1,
    "total_time_ms": 90.86,
    "scene_file": "scenes/scene_067.json",
    "image_file": "images/scene_067.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "0.25*x**2 + 1.0*y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "ellipse"
        },
        "c3": {
          "type": "ImplicitCurve",
          "expression": "-0.2*x**2 + y",
          "variables": [
            "x",
            "y"
          ]
        },
        "blend": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "0.25*x**2 + 1.0*y**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ImplicitCurve",
                "expression": "-0.2*x**2 + y",
                "variables": [
                  "x",
                  "y"
                ]
              }
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "c1": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "c2": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "c3": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "blend": {
          "color": "hsl(0, 70%, 50%)"
        }
      },
      "groups": {},
      "dependencies": {
        "c1": [
          "blend"
        ],
        "c2": [
          "blend"
        ],
        "c3": [
          "blend"
        ]
      },
      "reverse_dependencies": {
        "blend": [
          "c1",
          "c2",
          "c3"
        ]
      },
      "dependency_descriptions": {
        "blend": {
          "c1": "Evaluates hierarchical min blend wrapping child curve c1",
          "c2": "Evaluates hierarchical min blend wrapping child curve c2",
          "c3": "Evaluates hierarchical min blend wrapping child curve c3"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:46.852915",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_068",
    "name": "Hierarchical Blend Scene 2",
    "description": "Complex blended scalar field combining multiple curve types (Idx: 68).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 3,
    "fields_count": 1,
    "dependency_depth": 1,
    "total_time_ms": 92.82,
    "scene_file": "scenes/scene_068.json",
    "image_file": "images/scene_068.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1.44",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "0.25*x**2 + 0.826446280991735*y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "ellipse"
        },
        "c3": {
          "type": "ImplicitCurve",
          "expression": "-0.2*x**2 + y",
          "variables": [
            "x",
            "y"
          ]
        },
        "blend": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "0.25*x**2 + 0.826446280991735*y**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ImplicitCurve",
                "expression": "-0.2*x**2 + y",
                "variables": [
                  "x",
                  "y"
                ]
              }
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "c1": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "c2": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "c3": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "blend": {
          "color": "hsl(30, 70%, 50%)"
        }
      },
      "groups": {},
      "dependencies": {
        "c1": [
          "blend"
        ],
        "c2": [
          "blend"
        ],
        "c3": [
          "blend"
        ]
      },
      "reverse_dependencies": {
        "blend": [
          "c1",
          "c2",
          "c3"
        ]
      },
      "dependency_descriptions": {
        "blend": {
          "c1": "Evaluates hierarchical min blend wrapping child curve c1",
          "c2": "Evaluates hierarchical min blend wrapping child curve c2",
          "c3": "Evaluates hierarchical min blend wrapping child curve c3"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:46.958355",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_069",
    "name": "Hierarchical Blend Scene 3",
    "description": "Complex blended scalar field combining multiple curve types (Idx: 69).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 3,
    "fields_count": 1,
    "dependency_depth": 1,
    "total_time_ms": 129.74,
    "scene_file": "scenes/scene_069.json",
    "image_file": "images/scene_069.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1.96",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "0.25*x**2 + 0.694444444444444*y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "ellipse"
        },
        "c3": {
          "type": "ImplicitCurve",
          "expression": "-0.2*x**2 + y",
          "variables": [
            "x",
            "y"
          ]
        },
        "blend": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.96",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "0.25*x**2 + 0.694444444444444*y**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ImplicitCurve",
                "expression": "-0.2*x**2 + y",
                "variables": [
                  "x",
                  "y"
                ]
              }
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "c1": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "c2": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "c3": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "blend": {
          "color": "hsl(60, 70%, 50%)"
        }
      },
      "groups": {},
      "dependencies": {
        "c1": [
          "blend"
        ],
        "c2": [
          "blend"
        ],
        "c3": [
          "blend"
        ]
      },
      "reverse_dependencies": {
        "blend": [
          "c1",
          "c2",
          "c3"
        ]
      },
      "dependency_descriptions": {
        "blend": {
          "c1": "Evaluates hierarchical min blend wrapping child curve c1",
          "c2": "Evaluates hierarchical min blend wrapping child curve c2",
          "c3": "Evaluates hierarchical min blend wrapping child curve c3"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:47.061489",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_070",
    "name": "Hierarchical Blend Scene 4",
    "description": "Complex blended scalar field combining multiple curve types (Idx: 70).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 3,
    "fields_count": 1,
    "dependency_depth": 1,
    "total_time_ms": 104.56,
    "scene_file": "scenes/scene_070.json",
    "image_file": "images/scene_070.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 2.56",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "0.25*x**2 + 0.591715976331361*y**2 - 1",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "ellipse"
        },
        "c3": {
          "type": "ImplicitCurve",
          "expression": "-0.2*x**2 + y",
          "variables": [
            "x",
            "y"
          ]
        },
        "blend": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 2.56",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "0.25*x**2 + 0.591715976331361*y**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ImplicitCurve",
                "expression": "-0.2*x**2 + y",
                "variables": [
                  "x",
                  "y"
                ]
              }
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "c1": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "c2": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "c3": {
          "color": "#7f7f7f",
          "linewidth": 1.0,
          "linestyle": "dashed"
        },
        "blend": {
          "color": "hsl(90, 70%, 50%)"
        }
      },
      "groups": {},
      "dependencies": {
        "c1": [
          "blend"
        ],
        "c2": [
          "blend"
        ],
        "c3": [
          "blend"
        ]
      },
      "reverse_dependencies": {
        "blend": [
          "c1",
          "c2",
          "c3"
        ]
      },
      "dependency_descriptions": {
        "blend": {
          "c1": "Evaluates hierarchical min blend wrapping child curve c1",
          "c2": "Evaluates hierarchical min blend wrapping child curve c2",
          "c3": "Evaluates hierarchical min blend wrapping child curve c3"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:47.208844",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_071",
    "name": "Complex Dependent Scene 1",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 71).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 3,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 159.37,
    "scene_file": "scenes/scene_071.json",
    "image_file": "images/scene_071.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0"
        ],
        "c2": [
          "dep_0"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:47.332135",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_072",
    "name": "Complex Dependent Scene 2",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 72).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 4,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 131.22,
    "scene_file": "scenes/scene_072.json",
    "image_file": "images/scene_072.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1"
        ],
        "c2": [
          "dep_0",
          "dep_1"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:47.512527",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_073",
    "name": "Complex Dependent Scene 3",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 73).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 5,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 383.57,
    "scene_file": "scenes/scene_073.json",
    "image_file": "images/scene_073.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        },
        "dep_2": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1",
          "dep_2"
        ],
        "c2": [
          "dep_0",
          "dep_1",
          "dep_2"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ],
        "dep_2": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_2": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:47.662634",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_074",
    "name": "Complex Dependent Scene 4",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 74).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 6,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 337.42,
    "scene_file": "scenes/scene_074.json",
    "image_file": "images/scene_074.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_3": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        },
        "dep_2": {
          "color": "#ff7f0e"
        },
        "dep_3": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3"
        ],
        "c2": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ],
        "dep_2": [
          "c1",
          "c2"
        ],
        "dep_3": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_2": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_3": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:48.073169",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_075",
    "name": "Complex Dependent Scene 5",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 75).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 7,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 415.41,
    "scene_file": "scenes/scene_075.json",
    "image_file": "images/scene_075.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_3": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_4": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        },
        "dep_2": {
          "color": "#ff7f0e"
        },
        "dep_3": {
          "color": "#ff7f0e"
        },
        "dep_4": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4"
        ],
        "c2": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ],
        "dep_2": [
          "c1",
          "c2"
        ],
        "dep_3": [
          "c1",
          "c2"
        ],
        "dep_4": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_2": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_3": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_4": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:48.424785",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_076",
    "name": "Complex Dependent Scene 6",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 76).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 8,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 377.77,
    "scene_file": "scenes/scene_076.json",
    "image_file": "images/scene_076.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_3": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_4": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_5": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        },
        "dep_2": {
          "color": "#ff7f0e"
        },
        "dep_3": {
          "color": "#ff7f0e"
        },
        "dep_4": {
          "color": "#ff7f0e"
        },
        "dep_5": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5"
        ],
        "c2": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ],
        "dep_2": [
          "c1",
          "c2"
        ],
        "dep_3": [
          "c1",
          "c2"
        ],
        "dep_4": [
          "c1",
          "c2"
        ],
        "dep_5": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_2": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_3": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_4": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_5": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:48.853815",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_077",
    "name": "Complex Dependent Scene 7",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 77).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 9,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 395.06,
    "scene_file": "scenes/scene_077.json",
    "image_file": "images/scene_077.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_3": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_4": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_5": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_6": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 2.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        },
        "dep_2": {
          "color": "#ff7f0e"
        },
        "dep_3": {
          "color": "#ff7f0e"
        },
        "dep_4": {
          "color": "#ff7f0e"
        },
        "dep_5": {
          "color": "#ff7f0e"
        },
        "dep_6": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6"
        ],
        "c2": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ],
        "dep_2": [
          "c1",
          "c2"
        ],
        "dep_3": [
          "c1",
          "c2"
        ],
        "dep_4": [
          "c1",
          "c2"
        ],
        "dep_5": [
          "c1",
          "c2"
        ],
        "dep_6": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_2": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_3": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_4": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_5": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_6": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:49.247692",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_078",
    "name": "Complex Dependent Scene 8",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 78).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 10,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 509.39,
    "scene_file": "scenes/scene_078.json",
    "image_file": "images/scene_078.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_3": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_4": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_5": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_6": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 2.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_7": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 2.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        },
        "dep_2": {
          "color": "#ff7f0e"
        },
        "dep_3": {
          "color": "#ff7f0e"
        },
        "dep_4": {
          "color": "#ff7f0e"
        },
        "dep_5": {
          "color": "#ff7f0e"
        },
        "dep_6": {
          "color": "#ff7f0e"
        },
        "dep_7": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6",
          "dep_7"
        ],
        "c2": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6",
          "dep_7"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ],
        "dep_2": [
          "c1",
          "c2"
        ],
        "dep_3": [
          "c1",
          "c2"
        ],
        "dep_4": [
          "c1",
          "c2"
        ],
        "dep_5": [
          "c1",
          "c2"
        ],
        "dep_6": [
          "c1",
          "c2"
        ],
        "dep_7": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_2": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_3": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_4": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_5": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_6": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_7": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:49.657979",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_079",
    "name": "Complex Dependent Scene 9",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 79).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 11,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 593.38,
    "scene_file": "scenes/scene_079.json",
    "image_file": "images/scene_079.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_3": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_4": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_5": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_6": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 2.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_7": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 2.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_8": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 3.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        },
        "dep_2": {
          "color": "#ff7f0e"
        },
        "dep_3": {
          "color": "#ff7f0e"
        },
        "dep_4": {
          "color": "#ff7f0e"
        },
        "dep_5": {
          "color": "#ff7f0e"
        },
        "dep_6": {
          "color": "#ff7f0e"
        },
        "dep_7": {
          "color": "#ff7f0e"
        },
        "dep_8": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6",
          "dep_7",
          "dep_8"
        ],
        "c2": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6",
          "dep_7",
          "dep_8"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ],
        "dep_2": [
          "c1",
          "c2"
        ],
        "dep_3": [
          "c1",
          "c2"
        ],
        "dep_4": [
          "c1",
          "c2"
        ],
        "dep_5": [
          "c1",
          "c2"
        ],
        "dep_6": [
          "c1",
          "c2"
        ],
        "dep_7": [
          "c1",
          "c2"
        ],
        "dep_8": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_2": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_3": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_4": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_5": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_6": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_7": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_8": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:50.185007",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_080",
    "name": "Complex Dependent Scene 10",
    "description": "Deeply nested scene combining groups, dependencies, and composites (Idx: 80).",
    "complexity_tier": 5,
    "tier_name": "Deep Dependency Trees",
    "curves_count": 12,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 582.48,
    "scene_file": "scenes/scene_080.json",
    "image_file": "images/scene_080.png",
    "scene_data": {
      "objects": {
        "c1": {
          "type": "ConicSection",
          "expression": "y**2 + (x + 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c2": {
          "type": "ConicSection",
          "expression": "y**2 + (x - 1.5)**2 - 1.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_0": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "x**2 + (y + 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_3": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 0.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_4": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_5": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 1.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_6": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 2.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_7": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 2.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_8": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 3.0)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_9": {
          "type": "ConicSection",
          "expression": "x**2 + (y - 3.5)**2 - 0.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "c1": {
          "color": "#1f77b4"
        },
        "c2": {
          "color": "#2ca02c"
        },
        "dep_0": {
          "color": "#ff7f0e"
        },
        "dep_1": {
          "color": "#ff7f0e"
        },
        "dep_2": {
          "color": "#ff7f0e"
        },
        "dep_3": {
          "color": "#ff7f0e"
        },
        "dep_4": {
          "color": "#ff7f0e"
        },
        "dep_5": {
          "color": "#ff7f0e"
        },
        "dep_6": {
          "color": "#ff7f0e"
        },
        "dep_7": {
          "color": "#ff7f0e"
        },
        "dep_8": {
          "color": "#ff7f0e"
        },
        "dep_9": {
          "color": "#ff7f0e"
        }
      },
      "groups": {
        "sources": [
          "c1",
          "c2"
        ]
      },
      "dependencies": {
        "c1": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6",
          "dep_7",
          "dep_8",
          "dep_9"
        ],
        "c2": [
          "dep_0",
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6",
          "dep_7",
          "dep_8",
          "dep_9"
        ]
      },
      "reverse_dependencies": {
        "dep_0": [
          "c1",
          "c2"
        ],
        "dep_1": [
          "c1",
          "c2"
        ],
        "dep_2": [
          "c1",
          "c2"
        ],
        "dep_3": [
          "c1",
          "c2"
        ],
        "dep_4": [
          "c1",
          "c2"
        ],
        "dep_5": [
          "c1",
          "c2"
        ],
        "dep_6": [
          "c1",
          "c2"
        ],
        "dep_7": [
          "c1",
          "c2"
        ],
        "dep_8": [
          "c1",
          "c2"
        ],
        "dep_9": [
          "c1",
          "c2"
        ]
      },
      "dependency_descriptions": {
        "dep_0": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_1": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_2": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_3": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_4": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_5": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_6": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_7": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_8": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        },
        "dep_9": {
          "c1": "Coordinates propagate from c1 (source circle)",
          "c2": "Coordinates propagate from c2 (source circle)"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:50.796678",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_081",
    "name": "Dense Flower Stress Test (Petals=6)",
    "description": "Maximum stress test using a giant flower with 6 petals.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 192.36,
    "scene_file": "scenes/scene_081.json",
    "image_file": "images/scene_081.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.5*x - 0.866025403784438*y + 0.8)**2 + 25.0*(0.866025403784438*x - 0.5*y + 2.77555756156289e-16)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.4)**2 + (y - 0.692820323027551)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.8)**2 + (y - 9.79717439317883e-17)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.866025403784438*x + 0.5*y + 5.55111512312578e-17)**2 + 4.0*(0.5*x + 0.866025403784438*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.4)**2 + (y + 0.692820323027551)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 6,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#e377c2",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:09.009428",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_082",
    "name": "Dense Flower Stress Test (Petals=7)",
    "description": "Maximum stress test using a giant flower with 7 petals.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 209.39,
    "scene_file": "scenes/scene_082.json",
    "image_file": "images/scene_082.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.623489801858734*x - 0.78183148246803*y + 0.8)**2 + 25.0*(0.78183148246803*x - 0.623489801858734*y + 1.66533453693773e-16)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.178016747165051)**2 + (y - 0.779942329745459)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.720775094321935)**2 + (y - 0.347106991294047)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.433883739117558*x + 0.900968867902419*y + 1.11022302462516e-16)**2 + 4.0*(0.900968867902419*x + 0.433883739117558*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.178016747165052)**2 + (y + 0.779942329745459)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.498791841486987)**2 + (y + 0.625465185974424)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 7,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#e377c2",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:09.224568",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_083",
    "name": "Dense Flower Stress Test (Petals=8)",
    "description": "Maximum stress test using a giant flower with 8 petals.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 242.67,
    "scene_file": "scenes/scene_083.json",
    "image_file": "images/scene_083.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.707106781186548*x - 0.707106781186547*y + 0.8)**2 + 25.0*(0.707106781186547*x - 0.707106781186548*y + 1.66533453693773e-16)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 4.89858719658941e-17)**2 + (y - 0.8)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.565685424949238)**2 + (y - 0.565685424949238)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(2.44929359829471e-16*x + 1.0*y + 9.79717439317883e-17)**2 + 4.0*(1.0*x - 2.44929359829471e-16*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.565685424949238)**2 + (y + 0.565685424949238)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 1.46957615897682e-16)**2 + (y + 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.707106781186548*x - 0.707106781186547*y + 8.32667268468867e-16)**2 + 4.0*(-0.707106781186547*x + 0.707106781186548*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 8,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#e377c2",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:09.465463",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_084",
    "name": "Dense Flower Stress Test (Petals=9)",
    "description": "Maximum stress test using a giant flower with 9 petals.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 266.05,
    "scene_file": "scenes/scene_084.json",
    "image_file": "images/scene_084.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.766044443118978*x - 0.642787609686539*y + 0.8)**2 + 25.0*(0.642787609686539*x - 0.766044443118978*y - 5.55111512312578e-17)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.138918542133544)**2 + (y - 0.787846202409766)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.4)**2 + (y - 0.692820323027551)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(0.342020143325669*x + 0.939692620785908*y - 2.22044604925031e-16)**2 + 4.0*(0.939692620785908*x - 0.342020143325669*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.751754096628727)**2 + (y + 0.273616114660535)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.4)**2 + (y + 0.692820323027551)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.984807753012208*x - 0.17364817766693*y + 8.32667268468867e-17)**2 + 4.0*(-0.17364817766693*x + 0.984807753012208*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.612835554495182)**2 + (y + 0.514230087749232)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 9,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#e377c2",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:09.736823",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_085",
    "name": "Dense Flower Stress Test (Petals=10)",
    "description": "Maximum stress test using a giant flower with 10 petals.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 273.1,
    "scene_file": "scenes/scene_085.json",
    "image_file": "images/scene_085.png",
    "scene_data": {
      "objects": {
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(0.587785252292473*x - 0.809016994374947*y)**2 + 4.0*(-0.809016994374947*x - 0.587785252292473*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.247213595499958)**2 + (y - 0.760845213036123)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.247213595499958)**2 + (y - 0.760845213036123)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(0.587785252292473*x + 0.809016994374947*y + 1.11022302462516e-16)**2 + 4.0*(0.809016994374947*x - 0.587785252292473*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.8)**2 + (y - 9.79717439317883e-17)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.647213595499958)**2 + (y + 0.470228201833978)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.951056516295154*x + 0.309016994374948*y + 1.38777878078145e-16)**2 + 4.0*(0.309016994374948*x + 0.951056516295154*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.247213595499958)**2 + (y + 0.760845213036123)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.647213595499958)**2 + (y + 0.470228201833979)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 10,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "flower": {
          "color": "#e377c2",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:10.038178",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_086",
    "name": "Dense Spiral Stress Test (Turns=3)",
    "description": "Maximum stress test using a dense spiral approximation with 3 full turns.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 271.61,
    "scene_file": "scenes/scene_086.json",
    "image_file": "images/scene_086.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0694444444444444)**2 - 0.865933641975309",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.9305555555555556,
                  0.06944444444444442
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y - 0.0694444444444444)**2 - 0.741512345679012",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.9305555555555556,
                  0.06944444444444442
                ],
                [
                  -0.06944444444444442,
                  -0.7916666666666667
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y + 1.11022302462516e-16)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.06944444444444442,
                  -0.7916666666666667
                ],
                [
                  0.7222222222222222,
                  -1.1102230246251565e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y + 1.11022302462516e-16)**2 - 0.521604938271605",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.7222222222222222,
                  -1.1102230246251565e-16
                ],
                [
                  0.0,
                  0.7222222222222221
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0694444444444444)**2 - 0.426118827160494",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.7222222222222221
                ],
                [
                  -0.6527777777777777,
                  0.06944444444444442
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y - 0.0694444444444444)**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.6527777777777777,
                  0.06944444444444442
                ],
                [
                  -0.06944444444444442,
                  -0.5138888888888888
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0694444444444444)**2 - 0.264081790123457",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.06944444444444442,
                  -0.5138888888888888
                ],
                [
                  0.4444444444444444,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 0.197530864197531",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.4444444444444444,
                  0.0
                ],
                [
                  0.0,
                  0.4444444444444444
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0694444444444445)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.4444444444444444
                ],
                [
                  -0.3749999999999999,
                  0.06944444444444453
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y - 0.0694444444444445)**2 - 0.0933641975308641",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3749999999999999,
                  0.06944444444444453
                ],
                [
                  -0.06944444444444442,
                  -0.23611111111111094
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0694444444444444)**2 + (y - 1.11022302462516e-16)**2 - 0.0557484567901234",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.06944444444444442,
                  -0.23611111111111094
                ],
                [
                  0.16666666666666663,
                  1.1102230246251565e-16
                ]
              ]
            }
          ],
          "segment_count": 12,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:10.339601",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_087",
    "name": "Dense Spiral Stress Test (Turns=4)",
    "description": "Maximum stress test using a dense spiral approximation with 4 full turns.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 344.8,
    "scene_file": "scenes/scene_087.json",
    "image_file": "images/scene_087.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0520833333333334)**2 - 0.898546006944444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.9479166666666666,
                  0.05208333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333333)**2 + (y - 0.0520833333333334)**2 - 0.802517361111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.9479166666666666,
                  0.05208333333333337
                ],
                [
                  -0.05208333333333326,
                  -0.84375
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0520833333333333)**2 - 0.7119140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.05208333333333326,
                  -0.84375
                ],
                [
                  0.7916666666666667,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 1.11022302462516e-16)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.7916666666666667,
                  0.0
                ],
                [
                  1.1102230246251565e-16,
                  0.7916666666666666
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0520833333333334)**2 - 0.546983506944444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.7916666666666666
                ],
                [
                  -0.7395833333333331,
                  0.05208333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333331)**2 + (y - 0.0520833333333334)**2 - 0.47265625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.7395833333333331,
                  0.05208333333333337
                ],
                [
                  -0.05208333333333315,
                  -0.6354166666666666
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0520833333333331)**2 - 0.403754340277778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.05208333333333315,
                  -0.6354166666666666
                ],
                [
                  0.5833333333333335,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 2.22044604925031e-16)**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5833333333333335,
                  0.0
                ],
                [
                  2.220446049250313e-16,
                  0.5833333333333333
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 2.22044604925031e-16)**2 + (y - 0.0520833333333333)**2 - 0.2822265625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.220446049250313e-16,
                  0.5833333333333333
                ],
                [
                  -0.5312499999999998,
                  0.05208333333333326
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333331)**2 + (y - 0.0520833333333333)**2 - 0.229600694444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5312499999999998,
                  0.05208333333333326
                ],
                [
                  -0.05208333333333315,
                  -0.42708333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333331)**2 + (y + 1.11022302462516e-16)**2 - 0.182400173611111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.05208333333333315,
                  -0.42708333333333337
                ],
                [
                  0.3750000000000001,
                  -1.1102230246251565e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y + 1.11022302462516e-16)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.3750000000000001,
                  -1.1102230246251565e-16
                ],
                [
                  1.1102230246251565e-16,
                  0.3749999999999999
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0520833333333333)**2 - 0.104275173611111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.3749999999999999
                ],
                [
                  -0.3229166666666665,
                  0.05208333333333326
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333333)**2 + (y - 0.0520833333333333)**2 - 0.0733506944444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3229166666666665,
                  0.05208333333333326
                ],
                [
                  -0.05208333333333326,
                  -0.21875
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0520833333333333)**2 - 0.0478515625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.05208333333333326,
                  -0.21875
                ],
                [
                  0.16666666666666674,
                  0.0
                ]
              ]
            }
          ],
          "segment_count": 16,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:10.636693",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_088",
    "name": "Dense Spiral Stress Test (Turns=5)",
    "description": "Maximum stress test using a dense spiral approximation with 5 full turns.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 396.85,
    "scene_file": "scenes/scene_088.json",
    "image_file": "images/scene_088.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0416666666666666)**2 - 0.918402777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.9583333333333334,
                  0.04166666666666663
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0416666666666667)**2 + (y - 0.0416666666666666)**2 - 0.840277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.9583333333333334,
                  0.04166666666666663
                ],
                [
                  -0.04166666666666674,
                  -0.875
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0416666666666667)**2 - 0.765625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.04166666666666674,
                  -0.875
                ],
                [
                  0.8333333333333333,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 1.11022302462516e-16)**2 - 0.694444444444445",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8333333333333333,
                  0.0
                ],
                [
                  -1.1102230246251565e-16,
                  0.8333333333333334
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 1.11022302462516e-16)**2 + (y - 0.0416666666666667)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.1102230246251565e-16,
                  0.8333333333333334
                ],
                [
                  -0.7916666666666667,
                  0.04166666666666674
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0416666666666667)**2 + (y - 0.0416666666666667)**2 - 0.5625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.7916666666666667,
                  0.04166666666666674
                ],
                [
                  -0.04166666666666674,
                  -0.7083333333333333
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0416666666666667)**2 - 0.501736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.04166666666666674,
                  -0.7083333333333333
                ],
                [
                  0.6666666666666665,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 2.22044604925031e-16)**2 - 0.444444444444445",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.6666666666666665,
                  0.0
                ],
                [
                  -2.220446049250313e-16,
                  0.6666666666666667
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 2.22044604925031e-16)**2 + (y - 0.0416666666666667)**2 - 0.390625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.220446049250313e-16,
                  0.6666666666666667
                ],
                [
                  -0.6250000000000002,
                  0.04166666666666674
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.041666666666667)**2 + (y - 0.0416666666666667)**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.6250000000000002,
                  0.04166666666666674
                ],
                [
                  -0.04166666666666696,
                  -0.5416666666666665
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.041666666666667)**2 + (y - 2.22044604925031e-16)**2 - 0.293402777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.04166666666666696,
                  -0.5416666666666665
                ],
                [
                  0.4999999999999998,
                  2.220446049250313e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 2.22044604925031e-16)**2 + (y - 2.22044604925031e-16)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.4999999999999998,
                  2.220446049250313e-16
                ],
                [
                  -2.220446049250313e-16,
                  0.5000000000000002
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 2.22044604925031e-16)**2 + (y - 0.0416666666666669)**2 - 0.210069444444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.220446049250313e-16,
                  0.5000000000000002
                ],
                [
                  -0.4583333333333336,
                  0.04166666666666685
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.041666666666667)**2 + (y - 0.0416666666666669)**2 - 0.173611111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.4583333333333336,
                  0.04166666666666685
                ],
                [
                  -0.04166666666666696,
                  -0.3749999999999998
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.041666666666667)**2 + (y - 2.22044604925031e-16)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.04166666666666696,
                  -0.3749999999999998
                ],
                [
                  0.33333333333333304,
                  2.220446049250313e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 3.33066907387547e-16)**2 + (y - 2.22044604925031e-16)**2 - 0.111111111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.33333333333333304,
                  2.220446049250313e-16
                ],
                [
                  -3.3306690738754696e-16,
                  0.3333333333333336
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 3.33066907387547e-16)**2 + (y - 0.041666666666667)**2 - 0.0850694444444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -3.3306690738754696e-16,
                  0.3333333333333336
                ],
                [
                  -0.29166666666666696,
                  0.04166666666666696
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.041666666666667)**2 + (y - 0.041666666666667)**2 - 0.0625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.29166666666666696,
                  0.04166666666666696
                ],
                [
                  -0.04166666666666696,
                  -0.20833333333333304
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.041666666666667)**2 + (y - 3.33066907387547e-16)**2 - 0.0434027777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.04166666666666696,
                  -0.20833333333333304
                ],
                [
                  0.1666666666666664,
                  3.3306690738754696e-16
                ]
              ]
            }
          ],
          "segment_count": 20,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:11.005216",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_089",
    "name": "Dense Spiral Stress Test (Turns=6)",
    "description": "Maximum stress test using a dense spiral approximation with 6 full turns.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 491.53,
    "scene_file": "scenes/scene_089.json",
    "image_file": "images/scene_089.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0347222222222222)**2 - 0.931761188271605",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.9652777777777778,
                  0.03472222222222221
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222222)**2 + (y - 0.0347222222222222)**2 - 0.865933641975309",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.9652777777777778,
                  0.03472222222222221
                ],
                [
                  -0.03472222222222221,
                  -0.8958333333333334
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0347222222222222)**2 - 0.802517361111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.03472222222222221,
                  -0.8958333333333334
                ],
                [
                  0.8611111111111112,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 0.741512345679012",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8611111111111112,
                  0.0
                ],
                [
                  0.0,
                  0.8611111111111112
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0347222222222223)**2 - 0.682918595679012",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.8611111111111112
                ],
                [
                  -0.8263888888888888,
                  0.03472222222222232
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222222)**2 + (y - 0.0347222222222223)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8263888888888888,
                  0.03472222222222232
                ],
                [
                  -0.03472222222222221,
                  -0.7569444444444443
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222222)**2 + (y - 1.11022302462516e-16)**2 - 0.572964891975309",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.03472222222222221,
                  -0.7569444444444443
                ],
                [
                  0.7222222222222222,
                  1.1102230246251565e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 1.11022302462516e-16)**2 - 0.521604938271605",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.7222222222222222,
                  1.1102230246251565e-16
                ],
                [
                  0.0,
                  0.7222222222222223
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0347222222222223)**2 - 0.47265625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.7222222222222223
                ],
                [
                  -0.6875,
                  0.03472222222222232
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222223)**2 + (y - 0.0347222222222223)**2 - 0.426118827160494",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.6875,
                  0.03472222222222232
                ],
                [
                  -0.03472222222222232,
                  -0.6180555555555554
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222223)**2 + (y - 2.22044604925031e-16)**2 - 0.381992669753086",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.03472222222222232,
                  -0.6180555555555554
                ],
                [
                  0.5833333333333333,
                  2.220446049250313e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 2.22044604925031e-16)**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5833333333333333,
                  2.220446049250313e-16
                ],
                [
                  0.0,
                  0.5833333333333335
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0347222222222224)**2 - 0.300974151234568",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.5833333333333335
                ],
                [
                  -0.548611111111111,
                  0.03472222222222243
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222222)**2 + (y - 0.0347222222222224)**2 - 0.264081790123457",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.548611111111111,
                  0.03472222222222243
                ],
                [
                  -0.03472222222222221,
                  -0.4791666666666664
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222222)**2 + (y - 2.22044604925031e-16)**2 - 0.229600694444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.03472222222222221,
                  -0.4791666666666664
                ],
                [
                  0.4444444444444444,
                  2.220446049250313e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 2.22044604925031e-16)**2 - 0.197530864197531",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.4444444444444444,
                  2.220446049250313e-16
                ],
                [
                  0.0,
                  0.44444444444444464
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0347222222222224)**2 - 0.167872299382716",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.44444444444444464
                ],
                [
                  -0.4097222222222222,
                  0.03472222222222243
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222223)**2 + (y - 0.0347222222222224)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.4097222222222222,
                  0.03472222222222243
                ],
                [
                  -0.03472222222222232,
                  -0.34027777777777746
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222223)**2 + (y - 2.22044604925031e-16)**2 - 0.115788966049383",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.03472222222222232,
                  -0.34027777777777746
                ],
                [
                  0.30555555555555536,
                  2.220446049250313e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 1.11022302462516e-16)**2 + (y - 2.22044604925031e-16)**2 - 0.0933641975308641",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.30555555555555536,
                  2.220446049250313e-16
                ],
                [
                  -1.1102230246251565e-16,
                  0.3055555555555557
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 1.11022302462516e-16)**2 + (y - 0.0347222222222224)**2 - 0.0733506944444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.1102230246251565e-16,
                  0.3055555555555557
                ],
                [
                  -0.27083333333333337,
                  0.03472222222222243
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222223)**2 + (y - 0.0347222222222224)**2 - 0.0557484567901234",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.27083333333333337,
                  0.03472222222222243
                ],
                [
                  -0.03472222222222232,
                  -0.20138888888888862
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0347222222222223)**2 + (y - 2.22044604925031e-16)**2 - 0.0405574845679012",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.03472222222222232,
                  -0.20138888888888862
                ],
                [
                  0.16666666666666652,
                  2.220446049250313e-16
                ]
              ]
            }
          ],
          "segment_count": 24,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:11.432488",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_090",
    "name": "Dense Spiral Stress Test (Turns=7)",
    "description": "Maximum stress test using a dense spiral approximation with 7 full turns.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 1,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 532.06,
    "scene_file": "scenes/scene_090.json",
    "image_file": "images/scene_090.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0297619047619048)**2 - 0.941361961451247",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.9702380952380952,
                  0.029761904761904767
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619048)**2 + (y - 0.0297619047619048)**2 - 0.884495464852608",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.9702380952380952,
                  0.029761904761904767
                ],
                [
                  -0.029761904761904767,
                  -0.9107142857142857
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0297619047619048)**2 - 0.829400510204082",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.029761904761904767,
                  -0.9107142857142857
                ],
                [
                  0.8809523809523809,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 0.776077097505669",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.8809523809523809,
                  0.0
                ],
                [
                  0.0,
                  0.8809523809523809
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0297619047619048)**2 - 0.72452522675737",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  0.8809523809523809
                ],
                [
                  -0.8511904761904762,
                  0.029761904761904767
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619048)**2 + (y - 0.0297619047619048)**2 - 0.674744897959184",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.8511904761904762,
                  0.029761904761904767
                ],
                [
                  -0.029761904761904767,
                  -0.7916666666666666
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619048)**2 + (y - 1.11022302462516e-16)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.029761904761904767,
                  -0.7916666666666666
                ],
                [
                  0.761904761904762,
                  1.1102230246251565e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 1.11022302462516e-16)**2 - 0.580498866213152",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.761904761904762,
                  1.1102230246251565e-16
                ],
                [
                  1.1102230246251565e-16,
                  0.761904761904762
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0297619047619048)**2 - 0.536033163265306",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.761904761904762
                ],
                [
                  -0.7321428571428571,
                  0.029761904761904767
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619048)**2 + (y - 0.0297619047619048)**2 - 0.493339002267574",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.7321428571428571,
                  0.029761904761904767
                ],
                [
                  -0.029761904761904767,
                  -0.6726190476190476
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619048)**2 + (y - 1.11022302462516e-16)**2 - 0.452416383219955",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.029761904761904767,
                  -0.6726190476190476
                ],
                [
                  0.6428571428571429,
                  1.1102230246251565e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 1.11022302462516e-16)**2 - 0.413265306122449",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.6428571428571429,
                  1.1102230246251565e-16
                ],
                [
                  1.1102230246251565e-16,
                  0.6428571428571429
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0297619047619048)**2 - 0.375885770975057",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.6428571428571429
                ],
                [
                  -0.613095238095238,
                  0.029761904761904767
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619047)**2 + (y - 0.0297619047619048)**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.613095238095238,
                  0.029761904761904767
                ],
                [
                  -0.029761904761904656,
                  -0.5535714285714286
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0297619047619047)**2 - 0.306441326530612",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.029761904761904656,
                  -0.5535714285714286
                ],
                [
                  0.523809523809524,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 1.11022302462516e-16)**2 - 0.27437641723356",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.523809523809524,
                  0.0
                ],
                [
                  1.1102230246251565e-16,
                  0.5238095238095238
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0297619047619048)**2 - 0.244083049886621",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.5238095238095238
                ],
                [
                  -0.49404761904761896,
                  0.029761904761904767
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619047)**2 + (y - 0.0297619047619048)**2 - 0.215561224489796",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.49404761904761896,
                  0.029761904761904767
                ],
                [
                  -0.029761904761904656,
                  -0.43452380952380953
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0297619047619047)**2 - 0.188810941043084",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.029761904761904656,
                  -0.43452380952380953
                ],
                [
                  0.4047619047619049,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 1.11022302462516e-16)**2 - 0.163832199546485",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.4047619047619049,
                  0.0
                ],
                [
                  1.1102230246251565e-16,
                  0.40476190476190477
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0297619047619048)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.40476190476190477
                ],
                [
                  -0.3749999999999999,
                  0.029761904761904767
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619047)**2 + (y - 0.0297619047619048)**2 - 0.119189342403628",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3749999999999999,
                  0.029761904761904767
                ],
                [
                  -0.029761904761904656,
                  -0.31547619047619047
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0297619047619047)**2 - 0.0995252267573696",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.029761904761904656,
                  -0.31547619047619047
                ],
                [
                  0.2857142857142858,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 1.11022302462516e-16)**2 - 0.0816326530612245",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.2857142857142858,
                  0.0
                ],
                [
                  1.1102230246251565e-16,
                  0.2857142857142857
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0297619047619048)**2 - 0.0655116213151927",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.2857142857142857
                ],
                [
                  -0.2559523809523808,
                  0.029761904761904767
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0297619047619045)**2 + (y - 0.0297619047619048)**2 - 0.0511621315192744",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.2559523809523808,
                  0.029761904761904767
                ],
                [
                  -0.029761904761904545,
                  -0.1964285714285715
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0297619047619045)**2 - 0.0385841836734694",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.029761904761904545,
                  -0.1964285714285715
                ],
                [
                  0.16666666666666696,
                  0.0
                ]
              ]
            }
          ],
          "segment_count": 28,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:11.947193",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_091",
    "name": "Blended Field Stress (5 Circles)",
    "description": "Blended field combining 5 distinct overlapping circle fields with minimum union.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 0,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 85.68,
    "scene_file": "scenes/scene_091.json",
    "image_file": "images/scene_091.png",
    "scene_data": {
      "objects": {
        "blend_stress": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 1.5)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x - 0.463525491562421)**2 + (y - 1.42658477444273)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x + 1.21352549156242)**2 + (y - 0.88167787843871)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x + 1.21352549156242)**2 + (y + 0.88167787843871)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x - 0.463525491562421)**2 + (y + 1.42658477444273)**2 - 1.44",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            }
          ],
          "operation": "min"
        }
      },
      "styles": {
        "blend_stress": {
          "color": "#1f77b4",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:12.495041",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_092",
    "name": "Blended Field Stress (5 Circles Max)",
    "description": "Blended field combining 5 distinct overlapping circle fields with maximum intersection.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 0,
    "fields_count": 1,
    "dependency_depth": 0,
    "total_time_ms": 85.62,
    "scene_file": "scenes/scene_092.json",
    "image_file": "images/scene_092.png",
    "scene_data": {
      "objects": {
        "blend_stress": {
          "type": "BlendedField",
          "fields": [
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 1.0)**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x - 0.309016994374947)**2 + (y - 0.951056516295154)**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x + 0.809016994374947)**2 + (y - 0.587785252292473)**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x + 0.809016994374947)**2 + (y + 0.587785252292473)**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            },
            {
              "type": "CurveField",
              "curve": {
                "type": "ConicSection",
                "expression": "(x - 0.309016994374947)**2 + (y + 0.951056516295154)**2 - 2.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              }
            }
          ],
          "operation": "max"
        }
      },
      "styles": {
        "blend_stress": {
          "color": "#2ca02c",
          "linewidth": 2.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:12.597771",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_093",
    "name": "Superellipse Mesh Grid",
    "description": "A dense grid of 6 nested superellipses with varying parameters.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 6,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 126.87,
    "scene_file": "scenes/scene_093.json",
    "image_file": "images/scene_093.png",
    "scene_data": {
      "objects": {
        "se_1": {
          "type": "Superellipse",
          "expression": "4.0*Abs(x)**2.0 + 8.16326530612245*Abs(y)**2.0 - 1",
          "variables": [
            "x",
            "y"
          ],
          "a": 0.5,
          "b": 0.35,
          "n": 2.0,
          "shape_type": "ellipse"
        },
        "se_2": {
          "type": "Superellipse",
          "expression": "1.0*Abs(x)**2.5 + 2.43924205986611*Abs(y)**2.5 - 1",
          "variables": [
            "x",
            "y"
          ],
          "a": 1.0,
          "b": 0.7,
          "n": 2.5,
          "shape_type": "square-like"
        },
        "se_3": {
          "type": "Superellipse",
          "expression": "0.296296296296296*Abs(x)**3.0 + 0.863837598531477*Abs(y)**3.0 - 1",
          "variables": [
            "x",
            "y"
          ],
          "a": 1.5,
          "b": 1.0499999999999998,
          "n": 3.0,
          "shape_type": "square-like"
        },
        "se_4": {
          "type": "Superellipse",
          "expression": "0.0883883476483184*Abs(x)**3.5 + 0.308000821694066*Abs(y)**3.5 - 1",
          "variables": [
            "x",
            "y"
          ],
          "a": 2.0,
          "b": 1.4,
          "n": 3.5,
          "shape_type": "square-like"
        },
        "se_5": {
          "type": "Superellipse",
          "expression": "0.0256*Abs(x)**4.0 + 0.106622240733028*Abs(y)**4.0 - 1",
          "variables": [
            "x",
            "y"
          ],
          "a": 2.5,
          "b": 1.75,
          "n": 4.0,
          "shape_type": "square-like"
        },
        "se_6": {
          "type": "Superellipse",
          "expression": "0.00712778110110649*Abs(x)**4.5 + 0.035482415214975*Abs(y)**4.5 - 1",
          "variables": [
            "x",
            "y"
          ],
          "a": 3.0,
          "b": 2.0999999999999996,
          "n": 4.5,
          "shape_type": "square-like"
        }
      },
      "styles": {
        "se_1": {
          "color": "hsl(40, 65%, 55%)",
          "linewidth": 1.5
        },
        "se_2": {
          "color": "hsl(80, 65%, 55%)",
          "linewidth": 1.5
        },
        "se_3": {
          "color": "hsl(120, 65%, 55%)",
          "linewidth": 1.5
        },
        "se_4": {
          "color": "hsl(160, 65%, 55%)",
          "linewidth": 1.5
        },
        "se_5": {
          "color": "hsl(200, 65%, 55%)",
          "linewidth": 1.5
        },
        "se_6": {
          "color": "hsl(240, 65%, 55%)",
          "linewidth": 1.5
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:12.713253",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_094",
    "name": "Triple Flower Blended Pattern",
    "description": "Three multi-conic flowers overlapping in a line alignment.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 3,
    "fields_count": 0,
    "dependency_depth": 2,
    "total_time_ms": 1418.45,
    "scene_file": "scenes/scene_094.json",
    "image_file": "images/scene_094.png",
    "scene_data": {
      "objects": {
        "f1": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-1.83697019872103e-16*x - 1.0*y + 0.8)**2 + 25.0*(1.0*x - 1.83697019872103e-16*y + 9.79717439317882e-17)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.8)**2 + (y - 9.79717439317883e-17)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 1.46957615897682e-16)**2 + (y + 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "f2": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.309016994374948*x - 0.951056516295154*y + 0.8)**2 + 25.0*(0.951056516295154*x - 0.309016994374948*y + 8.32667268468867e-17)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.647213595499958)**2 + (y - 0.470228201833979)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.647213595499958)**2 + (y + 0.470228201833978)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.951056516295154*x - 0.309016994374947*y + 8.32667268468867e-17)**2 + 4.0*(-0.309016994374947*x + 0.951056516295154*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 5,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "f3": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.5*x - 0.866025403784438*y + 0.8)**2 + 25.0*(0.866025403784438*x - 0.5*y + 2.77555756156289e-16)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.4)**2 + (y - 0.692820323027551)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.8)**2 + (y - 9.79717439317883e-17)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.866025403784438*x + 0.5*y + 5.55111512312578e-17)**2 + 4.0*(0.5*x + 0.866025403784438*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.4)**2 + (y + 0.692820323027551)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 6,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "f1": {
          "color": "#aec7e8"
        },
        "f2": {
          "color": "#ffbb78"
        },
        "f3": {
          "color": "#98df8a"
        }
      },
      "groups": {},
      "dependencies": {
        "f1": [
          "f2"
        ],
        "f2": [
          "f3"
        ]
      },
      "reverse_dependencies": {
        "f2": [
          "f1"
        ],
        "f3": [
          "f2"
        ]
      },
      "dependency_descriptions": {
        "f2": {
          "f1": "f2.center offset dynamically from f1.center along x-axis"
        },
        "f3": {
          "f2": "f3.center offset dynamically from f2.center along x-axis"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:51.550380",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_095",
    "name": "Concentric Heart Ripple",
    "description": "Four nested heart shapes forming a beautiful ripple pattern.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 4,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 295.49,
    "scene_file": "scenes/scene_095.json",
    "image_file": "images/scene_095.png",
    "scene_data": {
      "objects": {
        "heart_1": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  0
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  1,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-x**2 + y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 2
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  0
                ],
                [
                  -1,
                  0
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "heart_2": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  0
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  1,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-x**2 + y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 2
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  0
                ],
                [
                  -1,
                  0
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "heart_3": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  0
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  1,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-x**2 + y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 2
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  0
                ],
                [
                  -1,
                  0
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "heart_4": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  0
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 0.5)**2 + (y - 0.25)**2 - 0.25",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  1,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-x**2 + y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 2
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  0
                ],
                [
                  -1,
                  0
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "heart_1": {
          "color": "#d62728",
          "linewidth": 1.2
        },
        "heart_2": {
          "color": "#d62728",
          "linewidth": 2.4
        },
        "heart_3": {
          "color": "#d62728",
          "linewidth": 3.5999999999999996
        },
        "heart_4": {
          "color": "#d62728",
          "linewidth": 4.8
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:13.273266",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_096",
    "name": "Occ SDF Hybrid Stress",
    "description": "A hybrid scene blending a circular occupancy field and a rectangular signed distance field.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 2,
    "fields_count": 2,
    "dependency_depth": 1,
    "total_time_ms": 890.63,
    "scene_file": "scenes/scene_096.json",
    "image_file": "images/scene_096.png",
    "scene_data": {
      "objects": {
        "circle_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 3.24",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.8,
                  0
                ],
                [
                  0,
                  1.8
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 3.24",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1.8
                ],
                [
                  -1.8,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 3.24",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.8,
                  0
                ],
                [
                  0,
                  -1.8
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 3.24",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  -1.8
                ],
                [
                  1.8,
                  0
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "rect_boundary": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  -1.5
                ],
                [
                  1.5,
                  -1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  -1.5
                ],
                [
                  1.5,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.5,
                  1.5
                ],
                [
                  -1.5,
                  1.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.5,
                  1.5
                ],
                [
                  -1.5,
                  -1.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.5,
            1.5,
            -1.5,
            1.5
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "occ": {
          "type": "OccupancyField",
          "region": {
            "type": "AreaRegion",
            "outer_boundary": {
              "type": "CompositeCurve",
              "segments": [
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 3.24",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      1.8,
                      0
                    ],
                    [
                      0,
                      1.8
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 3.24",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      0,
                      1.8
                    ],
                    [
                      -1.8,
                      0
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 3.24",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -1.8,
                      0
                    ],
                    [
                      0,
                      -1.8
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "ConicSection",
                    "expression": "x**2 + y**2 - 3.24",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "conic_type": "circle"
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      0,
                      -1.8
                    ],
                    [
                      1.8,
                      0
                    ]
                  ]
                }
              ],
              "segment_count": 4,
              "variables": [
                "x",
                "y"
              ],
              "is_square": false,
              "square_bounds": null,
              "is_convex_polygon": false,
              "convex_edges_abc": null,
              "polygon_vertices": null
            },
            "holes": []
          },
          "inside_value": 1.0,
          "outside_value": 0.0
        },
        "sdf": {
          "type": "SignedDistanceField",
          "region": {
            "type": "AreaRegion",
            "outer_boundary": {
              "type": "CompositeCurve",
              "segments": [
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "y + 1.5",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -1.5,
                      -1.5
                    ],
                    [
                      1.5,
                      -1.5
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "x - 1.5",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      1.5,
                      -1.5
                    ],
                    [
                      1.5,
                      1.5
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "y - 1.5",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      1.5,
                      1.5
                    ],
                    [
                      -1.5,
                      1.5
                    ]
                  ]
                },
                {
                  "type": "TrimmedImplicitCurve",
                  "base_curve": {
                    "type": "PolynomialCurve",
                    "expression": "x + 1.5",
                    "variables": [
                      "x",
                      "y"
                    ],
                    "degree": 1
                  },
                  "variables": [
                    "x",
                    "y"
                  ],
                  "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
                  "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
                  "endpoints": [
                    [
                      -1.5,
                      1.5
                    ],
                    [
                      -1.5,
                      -1.5
                    ]
                  ]
                }
              ],
              "segment_count": 4,
              "variables": [
                "x",
                "y"
              ],
              "is_square": true,
              "square_bounds": [
                -1.5,
                1.5,
                -1.5,
                1.5
              ],
              "is_convex_polygon": false,
              "convex_edges_abc": null,
              "polygon_vertices": null
            },
            "holes": []
          },
          "resolution": 0.1
        }
      },
      "styles": {
        "circle_boundary": {
          "color": "#1f77b4",
          "linewidth": 1.5,
          "linestyle": "dashed"
        },
        "rect_boundary": {
          "color": "#d62728",
          "linewidth": 1.5
        },
        "occ": {
          "color": "#1f77b4",
          "fill_alpha": 0.4
        },
        "sdf": {
          "color": "#d62728",
          "fill_alpha": 0.25
        }
      },
      "groups": {},
      "dependencies": {
        "occ": [
          "sdf"
        ]
      },
      "reverse_dependencies": {
        "sdf": [
          "occ"
        ]
      },
      "dependency_descriptions": {
        "sdf": {
          "occ": "SDF computes distance boundary representation from Occupancy Field occ"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:52.989009",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_097",
    "name": "Multi-Shape Starburst Grid",
    "description": "Giant combination of circle, square, triangle, L-shape, and T-shape together.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 5,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 310.31,
    "scene_file": "scenes/scene_097.json",
    "image_file": "images/scene_097.png",
    "scene_data": {
      "objects": {
        "c": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 6.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "s": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.8",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.8,
                  -1.8
                ],
                [
                  1.8,
                  -1.8
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1.8",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.8,
                  -1.8
                ],
                [
                  1.8,
                  1.8
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1.8",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.8,
                  1.8
                ],
                [
                  -1.8,
                  1.8
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.8",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.8,
                  1.8
                ],
                [
                  -1.8,
                  -1.8
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.8,
            1.8,
            -1.8,
            1.8
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "t": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  -0.5
                ],
                [
                  1,
                  -0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1,
                  -0.5
                ],
                [
                  0,
                  1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "-1.5*x + y - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  1
                ],
                [
                  -1,
                  -0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "l": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -1
                ],
                [
                  -0.5,
                  0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5,
                  -1
                ],
                [
                  0.5,
                  -1
                ]
              ]
            }
          ],
          "segment_count": 2,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "t_shape": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1,
                  0.5
                ],
                [
                  0,
                  0.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  0,
                  -1
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0,
                  0.5
                ],
                [
                  1,
                  0.5
                ]
              ]
            }
          ],
          "segment_count": 3,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "c": {
          "color": "#1f77b4"
        },
        "s": {
          "color": "#ff7f0e"
        },
        "t": {
          "color": "#2ca02c"
        },
        "l": {
          "color": "#d62728"
        },
        "t_shape": {
          "color": "#9467bd"
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:13.883433",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_098",
    "name": "Extreme Spiral Flower Blend",
    "description": "An ultimate blend of spiral approximation paths and a central conic flower.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 2,
    "fields_count": 0,
    "dependency_depth": 1,
    "total_time_ms": 1831.0,
    "scene_file": "scenes/scene_098.json",
    "image_file": "images/scene_098.png",
    "scene_data": {
      "objects": {
        "spiral": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + y**2 - 1.0",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0,
                  0.0
                ],
                [
                  0.0,
                  1.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "x**2 + (y - 0.0520833333333334)**2 - 0.898546006944444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.0,
                  1.0
                ],
                [
                  -0.9479166666666666,
                  0.05208333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333333)**2 + (y - 0.0520833333333334)**2 - 0.802517361111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.9479166666666666,
                  0.05208333333333337
                ],
                [
                  -0.05208333333333326,
                  -0.84375
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0520833333333333)**2 - 0.7119140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.05208333333333326,
                  -0.84375
                ],
                [
                  0.7916666666666667,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 1.11022302462516e-16)**2 - 0.626736111111111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.7916666666666667,
                  0.0
                ],
                [
                  1.1102230246251565e-16,
                  0.7916666666666666
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0520833333333334)**2 - 0.546983506944444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.7916666666666666
                ],
                [
                  -0.7395833333333331,
                  0.05208333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333331)**2 + (y - 0.0520833333333334)**2 - 0.47265625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.7395833333333331,
                  0.05208333333333337
                ],
                [
                  -0.05208333333333315,
                  -0.6354166666666666
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0520833333333331)**2 - 0.403754340277778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.05208333333333315,
                  -0.6354166666666666
                ],
                [
                  0.5833333333333335,
                  0.0
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 2.22044604925031e-16)**2 - 0.340277777777778",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.5833333333333335,
                  0.0
                ],
                [
                  2.220446049250313e-16,
                  0.5833333333333333
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 2.22044604925031e-16)**2 + (y - 0.0520833333333333)**2 - 0.2822265625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.220446049250313e-16,
                  0.5833333333333333
                ],
                [
                  -0.5312499999999998,
                  0.05208333333333326
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333331)**2 + (y - 0.0520833333333333)**2 - 0.229600694444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.5312499999999998,
                  0.05208333333333326
                ],
                [
                  -0.05208333333333315,
                  -0.42708333333333337
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333331)**2 + (y + 1.11022302462516e-16)**2 - 0.182400173611111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.05208333333333315,
                  -0.42708333333333337
                ],
                [
                  0.3750000000000001,
                  -1.1102230246251565e-16
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y + 1.11022302462516e-16)**2 - 0.140625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.3750000000000001,
                  -1.1102230246251565e-16
                ],
                [
                  1.1102230246251565e-16,
                  0.3749999999999999
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 1.11022302462516e-16)**2 + (y - 0.0520833333333333)**2 - 0.104275173611111",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.1102230246251565e-16,
                  0.3749999999999999
                ],
                [
                  -0.3229166666666665,
                  0.05208333333333326
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.0520833333333333)**2 + (y - 0.0520833333333333)**2 - 0.0733506944444444",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.3229166666666665,
                  0.05208333333333326
                ],
                [
                  -0.05208333333333326,
                  -0.21875
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x + 0.0520833333333333)**2 - 0.0478515625",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.05208333333333326,
                  -0.21875
                ],
                [
                  0.16666666666666674,
                  0.0
                ]
              ]
            }
          ],
          "segment_count": 16,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "flower": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "y**2 + (x - 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "4.0*(-0.707106781186548*x - 0.707106781186547*y + 0.8)**2 + 25.0*(0.707106781186547*x - 0.707106781186548*y + 1.66533453693773e-16)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x - 4.89858719658941e-17)**2 + (y - 0.8)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.565685424949238)**2 + (y - 0.565685424949238)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(2.44929359829471e-16*x + 1.0*y + 9.79717439317883e-17)**2 + 4.0*(1.0*x - 2.44929359829471e-16*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 0.565685424949238)**2 + (y + 0.565685424949238)**2 - 0.09",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "(x + 1.46957615897682e-16)**2 + (y + 0.8)**2 - 0.16",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "circle"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "ConicSection",
                "expression": "25.0*(-0.707106781186548*x - 0.707106781186547*y + 8.32667268468867e-16)**2 + 4.0*(-0.707106781186547*x + 0.707106781186548*y + 0.8)**2 - 1",
                "variables": [
                  "x",
                  "y"
                ],
                "conic_type": "ellipse"
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior."
            }
          ],
          "segment_count": 8,
          "variables": [
            "x",
            "y"
          ],
          "is_square": false,
          "square_bounds": null,
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        }
      },
      "styles": {
        "spiral": {
          "color": "#bcbd22"
        },
        "flower": {
          "color": "#e377c2",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {
        "spiral": [
          "flower"
        ]
      },
      "reverse_dependencies": {
        "flower": [
          "spiral"
        ]
      },
      "dependency_descriptions": {
        "flower": {
          "spiral": "flower coordinate system scales dynamically based on spiral shell radius"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:53.920521",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_099",
    "name": "Mega Dependency Web (10 Objects)",
    "description": "A massive dependency web containing a root object and 9 interdependent dependents.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 10,
    "fields_count": 0,
    "dependency_depth": 9,
    "total_time_ms": 538.37,
    "scene_file": "scenes/scene_099.json",
    "image_file": "images/scene_099.png",
    "scene_data": {
      "objects": {
        "root": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 4.0",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_1": {
          "type": "ConicSection",
          "expression": "(x - 0.81045345880221)**2 + (y - 1.26220647721184)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_2": {
          "type": "ConicSection",
          "expression": "(x + 0.624220254820714)**2 + (y - 1.36394614023852)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_3": {
          "type": "ConicSection",
          "expression": "(x + 1.48498874490067)**2 + (y - 0.211680012089801)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_4": {
          "type": "ConicSection",
          "expression": "(x + 0.980465431295418)**2 + (y + 1.13520374296189)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_5": {
          "type": "ConicSection",
          "expression": "(x - 0.425493278194839)**2 + (y + 1.43838641199471)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_6": {
          "type": "ConicSection",
          "expression": "(x - 1.44025542997555)**2 + (y + 0.419123247298389)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_7": {
          "type": "ConicSection",
          "expression": "(x - 1.13085338151496)**2 + (y - 0.985479898078184)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_8": {
          "type": "ConicSection",
          "expression": "(x + 0.21825005071292)**2 + (y - 1.48403736993507)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "dep_9": {
          "type": "ConicSection",
          "expression": "(x + 1.36669539282702)**2 + (y - 0.618177727862635)**2 - 0.09",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        }
      },
      "styles": {
        "root": {
          "color": "#1f77b4",
          "linewidth": 3
        },
        "dep_1": {
          "color": "#2ca02c"
        },
        "dep_2": {
          "color": "#2ca02c"
        },
        "dep_3": {
          "color": "#2ca02c"
        },
        "dep_4": {
          "color": "#2ca02c"
        },
        "dep_5": {
          "color": "#2ca02c"
        },
        "dep_6": {
          "color": "#2ca02c"
        },
        "dep_7": {
          "color": "#2ca02c"
        },
        "dep_8": {
          "color": "#2ca02c"
        },
        "dep_9": {
          "color": "#2ca02c"
        }
      },
      "groups": {},
      "dependencies": {
        "root": [
          "dep_1",
          "dep_2",
          "dep_3",
          "dep_4",
          "dep_5",
          "dep_6",
          "dep_7",
          "dep_8",
          "dep_9"
        ],
        "dep_1": [
          "dep_2"
        ],
        "dep_2": [
          "dep_3"
        ],
        "dep_3": [
          "dep_4"
        ],
        "dep_4": [
          "dep_5"
        ],
        "dep_5": [
          "dep_6"
        ],
        "dep_6": [
          "dep_7"
        ],
        "dep_7": [
          "dep_8"
        ],
        "dep_8": [
          "dep_9"
        ]
      },
      "reverse_dependencies": {
        "dep_1": [
          "root"
        ],
        "dep_2": [
          "root",
          "dep_1"
        ],
        "dep_3": [
          "root",
          "dep_2"
        ],
        "dep_4": [
          "root",
          "dep_3"
        ],
        "dep_5": [
          "root",
          "dep_4"
        ],
        "dep_6": [
          "root",
          "dep_5"
        ],
        "dep_7": [
          "root",
          "dep_6"
        ],
        "dep_8": [
          "root",
          "dep_7"
        ],
        "dep_9": [
          "root",
          "dep_8"
        ]
      },
      "dependency_descriptions": {
        "dep_1": {
          "root": "dep_1 propagates root translation"
        },
        "dep_2": {
          "root": "dep_2 propagates root translation",
          "dep_1": "dep_2 scales radius relative to preceding node dep_1"
        },
        "dep_3": {
          "root": "dep_3 propagates root translation",
          "dep_2": "dep_3 scales radius relative to preceding node dep_2"
        },
        "dep_4": {
          "root": "dep_4 propagates root translation",
          "dep_3": "dep_4 scales radius relative to preceding node dep_3"
        },
        "dep_5": {
          "root": "dep_5 propagates root translation",
          "dep_4": "dep_5 scales radius relative to preceding node dep_4"
        },
        "dep_6": {
          "root": "dep_6 propagates root translation",
          "dep_5": "dep_6 scales radius relative to preceding node dep_5"
        },
        "dep_7": {
          "root": "dep_7 propagates root translation",
          "dep_6": "dep_7 scales radius relative to preceding node dep_6"
        },
        "dep_8": {
          "root": "dep_8 propagates root translation",
          "dep_7": "dep_8 scales radius relative to preceding node dep_7"
        },
        "dep_9": {
          "root": "dep_9 propagates root translation",
          "dep_8": "dep_9 scales radius relative to preceding node dep_8"
        }
      },
      "metadata": {
        "created": "2026-05-22T17:50:55.794314",
        "version": "1.0"
      }
    }
  },
  {
    "id": "scene_100",
    "name": "The Ultimate 2Top stress Scene",
    "description": "The final ultimate stress scene combining 10 nested squares, 10 concentric circles, and 4 intersecting lines.",
    "complexity_tier": 6,
    "tier_name": "Extreme Complexity / Stress Tests",
    "curves_count": 22,
    "fields_count": 0,
    "dependency_depth": 0,
    "total_time_ms": 902.28,
    "scene_file": "scenes/scene_100.json",
    "image_file": "images/scene_100.png",
    "scene_data": {
      "objects": {
        "sq_1": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.35",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.35,
                  -0.35
                ],
                [
                  0.35,
                  -0.35
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 0.35",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.35,
                  -0.35
                ],
                [
                  0.35,
                  0.35
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.35",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.35,
                  0.35
                ],
                [
                  -0.35,
                  0.35
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 0.35",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.35,
                  0.35
                ],
                [
                  -0.35,
                  -0.35
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -0.35,
            0.35,
            -0.35,
            0.35
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_2": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 0.7",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.7,
                  -0.7
                ],
                [
                  0.7,
                  -0.7
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 0.7",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.7,
                  -0.7
                ],
                [
                  0.7,
                  0.7
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 0.7",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  0.7,
                  0.7
                ],
                [
                  -0.7,
                  0.7
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 0.7",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -0.7,
                  0.7
                ],
                [
                  -0.7,
                  -0.7
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -0.7,
            0.7,
            -0.7,
            0.7
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_3": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.05",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.0499999999999998,
                  -1.0499999999999998
                ],
                [
                  1.0499999999999998,
                  -1.0499999999999998
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1.05",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0499999999999998,
                  -1.0499999999999998
                ],
                [
                  1.0499999999999998,
                  1.0499999999999998
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1.05",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.0499999999999998,
                  1.0499999999999998
                ],
                [
                  -1.0499999999999998,
                  1.0499999999999998
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.05",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.0499999999999998,
                  1.0499999999999998
                ],
                [
                  -1.0499999999999998,
                  -1.0499999999999998
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.0499999999999998,
            1.0499999999999998,
            -1.0499999999999998,
            1.0499999999999998
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_4": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.4",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.4,
                  -1.4
                ],
                [
                  1.4,
                  -1.4
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1.4",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.4,
                  -1.4
                ],
                [
                  1.4,
                  1.4
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1.4",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.4,
                  1.4
                ],
                [
                  -1.4,
                  1.4
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.4",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.4,
                  1.4
                ],
                [
                  -1.4,
                  -1.4
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.4,
            1.4,
            -1.4,
            1.4
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_5": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 1.75",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.75,
                  -1.75
                ],
                [
                  1.75,
                  -1.75
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 1.75",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.75,
                  -1.75
                ],
                [
                  1.75,
                  1.75
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 1.75",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  1.75,
                  1.75
                ],
                [
                  -1.75,
                  1.75
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 1.75",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -1.75,
                  1.75
                ],
                [
                  -1.75,
                  -1.75
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -1.75,
            1.75,
            -1.75,
            1.75
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_6": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 2.1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0999999999999996,
                  -2.0999999999999996
                ],
                [
                  2.0999999999999996,
                  -2.0999999999999996
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 2.1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0999999999999996,
                  -2.0999999999999996
                ],
                [
                  2.0999999999999996,
                  2.0999999999999996
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 2.1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.0999999999999996,
                  2.0999999999999996
                ],
                [
                  -2.0999999999999996,
                  2.0999999999999996
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 2.1",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.0999999999999996,
                  2.0999999999999996
                ],
                [
                  -2.0999999999999996,
                  -2.0999999999999996
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -2.0999999999999996,
            2.0999999999999996,
            -2.0999999999999996,
            2.0999999999999996
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_7": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 2.45",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.4499999999999997,
                  -2.4499999999999997
                ],
                [
                  2.4499999999999997,
                  -2.4499999999999997
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 2.45",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.4499999999999997,
                  -2.4499999999999997
                ],
                [
                  2.4499999999999997,
                  2.4499999999999997
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 2.45",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.4499999999999997,
                  2.4499999999999997
                ],
                [
                  -2.4499999999999997,
                  2.4499999999999997
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 2.45",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.4499999999999997,
                  2.4499999999999997
                ],
                [
                  -2.4499999999999997,
                  -2.4499999999999997
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -2.4499999999999997,
            2.4499999999999997,
            -2.4499999999999997,
            2.4499999999999997
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_8": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 2.8",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.8,
                  -2.8
                ],
                [
                  2.8,
                  -2.8
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 2.8",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.8,
                  -2.8
                ],
                [
                  2.8,
                  2.8
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 2.8",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  2.8,
                  2.8
                ],
                [
                  -2.8,
                  2.8
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 2.8",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -2.8,
                  2.8
                ],
                [
                  -2.8,
                  -2.8
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -2.8,
            2.8,
            -2.8,
            2.8
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_9": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 3.15",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -3.15,
                  -3.15
                ],
                [
                  3.15,
                  -3.15
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 3.15",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  3.15,
                  -3.15
                ],
                [
                  3.15,
                  3.15
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 3.15",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  3.15,
                  3.15
                ],
                [
                  -3.15,
                  3.15
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 3.15",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -3.15,
                  3.15
                ],
                [
                  -3.15,
                  -3.15
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -3.15,
            3.15,
            -3.15,
            3.15
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "sq_10": {
          "type": "CompositeCurve",
          "segments": [
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y + 3.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -3.5,
                  -3.5
                ],
                [
                  3.5,
                  -3.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x - 3.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  3.5,
                  -3.5
                ],
                [
                  3.5,
                  3.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "y - 3.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  3.5,
                  3.5
                ],
                [
                  -3.5,
                  3.5
                ]
              ]
            },
            {
              "type": "TrimmedImplicitCurve",
              "base_curve": {
                "type": "PolynomialCurve",
                "expression": "x + 3.5",
                "variables": [
                  "x",
                  "y"
                ],
                "degree": 1
              },
              "variables": [
                "x",
                "y"
              ],
              "mask": "<<FUNCTION_NOT_SERIALIZABLE>>",
              "mask_description": "Mask function cannot be serialized. Manual reconstruction required to restore original mask behavior.",
              "endpoints": [
                [
                  -3.5,
                  3.5
                ],
                [
                  -3.5,
                  -3.5
                ]
              ]
            }
          ],
          "segment_count": 4,
          "variables": [
            "x",
            "y"
          ],
          "is_square": true,
          "square_bounds": [
            -3.5,
            3.5,
            -3.5,
            3.5
          ],
          "is_convex_polygon": false,
          "convex_edges_abc": null,
          "polygon_vertices": null
        },
        "c_1": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.1225",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_2": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 0.49",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_3": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1.1025",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_4": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 1.96",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_5": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 3.0625",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_6": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 4.41",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_7": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 6.0025",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_8": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 7.84",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_9": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 9.9225",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "c_10": {
          "type": "ConicSection",
          "expression": "x**2 + y**2 - 12.25",
          "variables": [
            "x",
            "y"
          ],
          "conic_type": "circle"
        },
        "l1": {
          "type": "ImplicitCurve",
          "expression": "x - y",
          "variables": [
            "x",
            "y"
          ]
        },
        "l2": {
          "type": "ImplicitCurve",
          "expression": "x + y",
          "variables": [
            "x",
            "y"
          ]
        }
      },
      "styles": {
        "sq_1": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_2": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_3": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_4": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_5": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_6": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_7": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_8": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_9": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "sq_10": {
          "color": "#aec7e8",
          "linewidth": 1
        },
        "c_1": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_2": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_3": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_4": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_5": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_6": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_7": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_8": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_9": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "c_10": {
          "color": "#ffbb78",
          "linewidth": 1
        },
        "l1": {
          "color": "#d62728",
          "linewidth": 2
        },
        "l2": {
          "color": "#2ca02c",
          "linewidth": 2
        }
      },
      "groups": {},
      "dependencies": {},
      "reverse_dependencies": {},
      "metadata": {
        "created": "2026-05-22T17:45:14.912070",
        "version": "1.0"
      }
    }
  }
];
