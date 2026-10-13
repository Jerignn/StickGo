// StickGo animation data: which sprite frames play, how fast, and when attacks hit.
// Edit it with anim-editor.html (it saves this file) or by hand. index.html reads it at start-up.
//  hero.states  - what he does when he isn't attacking (frames = sheet frame numbers, fps = speed)
//  hero.actions - attacks and skills: parts play one after another; hits land when the part reaches
//                 frame number `at` (a position in that part's frame list); front/back = reach in
//                 game units, kb = shove, cd = cooldown (s), lunge = step forward, flash = frames
//                 that fill the screen
//  foes         - stats and animations for every enemy kind; row/frames pick cells in pictures/foe_<kind>.png
window.STICKGO_ANIMS = {
  "hero": {
    "states": {
      "idle": {
        "sheet": "idle",
        "frames": [0, 1, 2, 3],
        "fps": 6
      },
      "run": {
        "sheet": "run",
        "frames": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        "fps": 16
      },
      "jump": {
        "sheet": "jump",
        "frames": [0, 1, 2]
      },
      "jump_peak": {
        "sheet": "jump_peak",
        "frames": [0, 1, 2],
        "fps": 8
      },
      "fall": {
        "sheet": "fall",
        "frames": [0, 1, 2, 3],
        "fps": 11
      },
      "dash": {
        "sheet": "dash",
        "frames": [4, 5, 6, 7, 8]
      },
      "hurt": {
        "sheet": "hit1",
        "frames": [0, 1, 2]
      },
      "dying": {
        "sheet": "hit3",
        "frames": [0, 1, 2],
        "fps": 6
      }
    },
    "actions": {
      "attack1": {
        "label": "ATTACK 1",
        "basic": true,
        "lunge": 70,
        "parts": [
          {
            "sheet": "attack1",
            "frames": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "fps": 26
          }
        ],
        "hits": [
          {
            "at": 3,
            "dmg": 14,
            "front": 82,
            "back": 8,
            "kb": 34
          }
        ]
      },
      "attack2": {
        "label": "ATTACK 2",
        "basic": true,
        "lunge": 70,
        "parts": [
          {
            "sheet": "attack2",
            "frames": [0, 1, 2, 3, 4, 5, 6, 7],
            "fps": 26
          }
        ],
        "hits": [
          {
            "at": 1,
            "dmg": 14,
            "front": 82,
            "back": 8,
            "kb": 34
          }
        ]
      },
      "attack3": {
        "label": "ATTACK 3",
        "basic": true,
        "lunge": 50,
        "parts": [
          {
            "sheet": "attack3",
            "frames": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "fps": 24
          }
        ],
        "hits": [
          {
            "at": 2,
            "dmg": 26,
            "front": 96,
            "back": 30,
            "kb": 60
          }
        ]
      },
      "skill1": {
        "label": "SKILL 1 - SLAM",
        "skill": true,
        "cd": 4,
        "parts": [
          {
            "sheet": "skill1",
            "frames": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "fps": 13
          }
        ],
        "hits": [
          {
            "at": 4,
            "dmg": 42,
            "front": 165,
            "back": 0,
            "kb": 90
          }
        ]
      },
      "skill2": {
        "label": "SKILL 2 - SPIN",
        "skill": true,
        "cd": 8,
        "invuln": true,
        "parts": [
          {
            "sheet": "skill2",
            "frames": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            "fps": 22
          }
        ],
        "hits": [
          {
            "at": 2,
            "dmg": 16,
            "front": 130,
            "back": 130,
            "kb": 26
          },
          {
            "at": 4,
            "dmg": 16,
            "front": 130,
            "back": 130,
            "kb": 26
          },
          {
            "at": 6,
            "dmg": 16,
            "front": 130,
            "back": 130,
            "kb": 26
          },
          {
            "at": 8,
            "dmg": 16,
            "front": 130,
            "back": 130,
            "kb": 26
          }
        ]
      },
      "skill3": {
        "label": "SKILL 3 - ULTIMATE",
        "skill": true,
        "cd": 18,
        "invuln": true,
        "parts": [
          {
            "sheet": "start_skill3",
            "frames": [0, 1, 2],
            "fps": 8
          },
          {
            "sheet": "skill3",
            "frames": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "fps": 15,
            "flash": [14, 15, 16, 17, 18]
          }
        ],
        "hits": [
          {
            "part": 1,
            "at": 16,
            "dmg": 130,
            "front": 2000,
            "back": 2000,
            "kb": 0,
            "screen": true
          }
        ]
      }
    },
    "combo": ["attack1", "attack2", "attack3"],
    "skills": ["skill1", "skill2", "skill3"]
  },
  "foes": {
    "grunt": {
      "stats": {
        "hp": 30,
        "speed": 110,
        "dmg": 10,
        "stand": 40,
        "windup": 0.5,
        "rec": 0.5,
        "gold": [1, 3],
        "pts": 10
      },
      "anims": {
        "idle": {
          "row": 0,
          "frames": [0, 1, 2, 3],
          "fps": 6
        },
        "walk": {
          "row": 1,
          "frames": [0, 1, 2, 3, 4, 5, 6, 7]
        },
        "windup": {
          "row": 2,
          "frames": [0, 1, 2]
        },
        "strike": {
          "row": 2,
          "frames": [3, 4, 5]
        },
        "release": {
          "row": 2,
          "frames": [3, 4, 5],
          "fps": 8
        },
        "charge": {
          "row": 2,
          "frames": [4]
        },
        "hit": {
          "row": 3,
          "frames": [0, 1]
        },
        "death": {
          "row": 4,
          "frames": [0, 1, 2, 3, 4, 5],
          "fps": 10
        }
      }
    },
    "ninja": {
      "stats": {
        "hp": 22,
        "speed": 150,
        "dmg": 14,
        "stand": 260,
        "windup": 0.55,
        "rec": 0.9,
        "gold": [2, 4],
        "pts": 15
      },
      "anims": {
        "idle": {
          "row": 0,
          "frames": [0, 1, 2, 3],
          "fps": 6
        },
        "walk": {
          "row": 1,
          "frames": [0, 1, 2, 3, 4, 5, 6, 7]
        },
        "windup": {
          "row": 2,
          "frames": [0, 1, 2]
        },
        "strike": {
          "row": 2,
          "frames": [3, 4, 5]
        },
        "release": {
          "row": 2,
          "frames": [3, 4, 5],
          "fps": 8
        },
        "charge": {
          "row": 2,
          "frames": [4]
        },
        "hit": {
          "row": 3,
          "frames": [0, 1]
        },
        "death": {
          "row": 4,
          "frames": [0, 1, 2, 3, 4, 5],
          "fps": 10
        }
      }
    },
    "guard": {
      "stats": {
        "hp": 50,
        "speed": 75,
        "dmg": 14,
        "stand": 40,
        "windup": 0.55,
        "rec": 0.6,
        "gold": [4, 6],
        "pts": 25
      },
      "anims": {
        "idle": {
          "row": 0,
          "frames": [0, 1, 2, 3],
          "fps": 6
        },
        "walk": {
          "row": 1,
          "frames": [0, 1, 2, 3, 4, 5, 6, 7]
        },
        "windup": {
          "row": 2,
          "frames": [0, 1, 2]
        },
        "strike": {
          "row": 2,
          "frames": [3, 4, 5]
        },
        "release": {
          "row": 2,
          "frames": [3, 4, 5],
          "fps": 8
        },
        "charge": {
          "row": 2,
          "frames": [4]
        },
        "hit": {
          "row": 3,
          "frames": [0, 1]
        },
        "death": {
          "row": 4,
          "frames": [0, 1, 2, 3, 4, 5],
          "fps": 10
        }
      }
    },
    "brute": {
      "stats": {
        "hp": 90,
        "speed": 65,
        "dmg": 22,
        "stand": 150,
        "windup": 0.85,
        "rec": 0.9,
        "gold": [8, 10],
        "pts": 40
      },
      "anims": {
        "idle": {
          "row": 0,
          "frames": [0, 1, 2, 3],
          "fps": 6
        },
        "walk": {
          "row": 1,
          "frames": [0, 1, 2, 3, 4, 5, 6, 7]
        },
        "windup": {
          "row": 2,
          "frames": [0, 1, 2]
        },
        "strike": {
          "row": 2,
          "frames": [3, 4, 5]
        },
        "release": {
          "row": 2,
          "frames": [3, 4, 5],
          "fps": 8
        },
        "charge": {
          "row": 2,
          "frames": [4]
        },
        "hit": {
          "row": 3,
          "frames": [0, 1]
        },
        "death": {
          "row": 4,
          "frames": [0, 1, 2, 3, 4, 5],
          "fps": 10
        }
      }
    },
    "archer": {
      "stats": {
        "hp": 20,
        "speed": 90,
        "dmg": 12,
        "stand": 330,
        "windup": 0.7,
        "rec": 1.2,
        "gold": [3, 5],
        "pts": 20
      },
      "anims": {
        "idle": {
          "row": 0,
          "frames": [0, 1, 2, 3],
          "fps": 6
        },
        "walk": {
          "row": 1,
          "frames": [0, 1, 2, 3, 4, 5, 6, 7]
        },
        "windup": {
          "row": 2,
          "frames": [0, 1, 2]
        },
        "strike": {
          "row": 2,
          "frames": [3, 4, 5]
        },
        "release": {
          "row": 2,
          "frames": [3, 4, 5],
          "fps": 8
        },
        "charge": {
          "row": 2,
          "frames": [4]
        },
        "hit": {
          "row": 3,
          "frames": [0, 1]
        },
        "death": {
          "row": 4,
          "frames": [0, 1, 2, 3, 4, 5],
          "fps": 10
        }
      }
    },
    "bomber": {
      "stats": {
        "hp": 20,
        "speed": 80,
        "dmg": 20,
        "stand": 280,
        "windup": 0.8,
        "rec": 1.6,
        "gold": [3, 5],
        "pts": 20
      },
      "anims": {
        "idle": {
          "row": 0,
          "frames": [0, 1, 2, 3],
          "fps": 6
        },
        "walk": {
          "row": 1,
          "frames": [0, 1, 2, 3, 4, 5, 6, 7]
        },
        "windup": {
          "row": 2,
          "frames": [0, 1, 2]
        },
        "strike": {
          "row": 2,
          "frames": [3, 4, 5]
        },
        "release": {
          "row": 2,
          "frames": [3, 4, 5],
          "fps": 8
        },
        "charge": {
          "row": 2,
          "frames": [4]
        },
        "hit": {
          "row": 3,
          "frames": [0, 1]
        },
        "death": {
          "row": 4,
          "frames": [0, 1, 2, 3, 4, 5],
          "fps": 10
        }
      }
    },
    "ghost": {
      "stats": {
        "hp": 26,
        "speed": 100,
        "dmg": 14,
        "stand": 40,
        "windup": 0.5,
        "rec": 0.5,
        "gold": [4, 6],
        "pts": 25
      },
      "anims": {
        "idle": {
          "row": 0,
          "frames": [0, 1, 2, 3],
          "fps": 6
        },
        "walk": {
          "row": 1,
          "frames": [0, 1, 2, 3, 4, 5, 6, 7]
        },
        "windup": {
          "row": 2,
          "frames": [0, 1, 2]
        },
        "strike": {
          "row": 2,
          "frames": [3, 4, 5]
        },
        "release": {
          "row": 2,
          "frames": [3, 4, 5],
          "fps": 8
        },
        "charge": {
          "row": 2,
          "frames": [4]
        },
        "hit": {
          "row": 3,
          "frames": [0, 1]
        },
        "death": {
          "row": 4,
          "frames": [0, 1, 2, 3, 4, 5],
          "fps": 10
        }
      }
    },
    "boss": {
      "stats": {
        "hp": 320,
        "speed": 60,
        "dmg": 28,
        "stand": 190,
        "windup": 0.9,
        "rec": 1,
        "gold": [60, 60],
        "pts": 200
      },
      "anims": {
        "idle": {
          "row": 0,
          "frames": [0, 1, 2, 3],
          "fps": 6
        },
        "walk": {
          "row": 1,
          "frames": [0, 1, 2, 3, 4, 5, 6, 7]
        },
        "windup": {
          "row": 2,
          "frames": [0, 1, 2]
        },
        "strike": {
          "row": 2,
          "frames": [3, 4, 5]
        },
        "release": {
          "row": 2,
          "frames": [3, 4, 5],
          "fps": 8
        },
        "charge": {
          "row": 2,
          "frames": [4]
        },
        "hit": {
          "row": 3,
          "frames": [0, 1]
        },
        "death": {
          "row": 4,
          "frames": [0, 1, 2, 3, 4, 5],
          "fps": 10
        }
      }
    }
  }
};
