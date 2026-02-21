# Data Model: Conic Section Fix

## Overview
This document describes the data model for the conic section implementation that needs to be fixed in the 2Top 2D Implicit Geometry Library.

## Entities

### ConicSection
- **name** (string): Name of the conic section
- **expression** (sympy.Expr): Mathematical expression defining the conic section
- **variables** (tuple): Tuple of sympy symbols representing the variables (typically x, y)
- **conic_type** (string): Type of conic section (circle, ellipse, parabola, hyperbola)
- **coefficients** (dict): Dictionary of coefficients from the general conic form Ax² + Bxy + Cy² + Dx + Ey + F = 0

## Relationships
- A **ConicSection** is defined by a mathematical expression
- A **ConicSection** has a specific **conic_type** that determines its properties
- A **ConicSection** has associated **coefficients** for mathematical operations

## Properties to Fix
The following properties need to be corrected in the implementation:
1. **Conic Type Classification** - Ensure proper mathematical classification using discriminant analysis
2. **Coefficient Extraction** - Ensure accurate extraction of coefficients from expressions
3. **Bounding Box Calculation** - Ensure proper calculation for all conic types
4. **Point Containment Testing** - Ensure accurate testing of point membership
5. **Evaluation Methods** - Ensure correct evaluation of conic equations