"""World-specific inputs/operators; common stages live in world_gate."""
SPEC = {'component': 'input_world',
 'legacy': 'world_cases.legacy_input',
 'api': {'api': {'suites': ['dos_input', 'scene', 'video', 'game_services', 'menu'],
                 'filter': True,
                 'extra_names': ['EditLevelPassword', 'InsertHighScoreAndClearScore'],
                 'expected_cases': 184,
                 'allowed_rejections': []}},
 'defects': [{'kind': 'historical-case', 'id': 'dropped-scan'},
             {'kind': 'historical-case', 'id': 'missed-serialization'},
             {'kind': 'historical-case', 'id': 'swapped-make-break'},
             {'kind': 'historical-case', 'id': 'lost-E0-prefix'},
             {'kind': 'historical-case', 'id': 'stale-joystick-count'}],
 'worlds_enabled': ['timing_world', 'audio_world', 'palette_world', 'input_world']}
