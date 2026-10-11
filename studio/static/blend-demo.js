/** Static composition sample, mirrored by examples/tidal_atlas_confluence.json. */
export const blendDemoRecipe = {
  "schema_version": 3,
  "title": "Confluence study",
  "objects": [
    {
      "id": "island_ember",
      "name": "Solstice",
      "type": "island",
      "parameters": {
        "x": 300,
        "y": 350,
        "radius": 175,
        "elongation": 1.05,
        "rotation": -15,
        "lobes": 3,
        "warp": 0.25,
        "phase": 0.4
      },
      "style": {
        "palette": "ember",
        "opacity": 1,
        "visible": true
      },
      "keyframes": []
    },
    {
      "id": "island_lagoon",
      "name": "Undertow",
      "type": "island",
      "parameters": {
        "x": 700,
        "y": 350,
        "radius": 175,
        "elongation": 1.1,
        "rotation": 145,
        "lobes": 3,
        "warp": 0.2,
        "phase": 2.2
      },
      "style": {
        "palette": "lagoon",
        "opacity": 1,
        "visible": true
      },
      "keyframes": []
    }
  ],
  "blends": [
    {
      "id": "blend_confluence",
      "name": "Confluence",
      "source_a": "island_ember",
      "source_b": "island_lagoon",
      "operation": "smooth_union",
      "amount": 0.85,
      "style": {
        "palette": "aurora",
        "opacity": 1,
        "visible": true
      }
    }
  ],
  "view": {
    "zoom": 1,
    "pan_x": 0,
    "pan_y": 0,
    "grid": false,
    "contours": 24
  },
  "animation": {
    "playing": false,
    "time": 0,
    "speed": 1,
    "motion": 0
  }
};
