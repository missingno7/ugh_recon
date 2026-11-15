"""World-specific inputs/operators; common stages live in world_gate."""
SPEC = {'component': 'palette_world',
 'legacy': 'world_cases.legacy_palette',
 'api': {'api': {'suites': ['video', 'video_upload', 'render_primitives', 'render'],
                 'filter': False,
                 'expected_cases': 1118,
                 'allowed_rejections': []}},
 'defects': [{'kind': 'historical-case', 'id': 'missed-serialization'},
             {'kind': 'historical-case', 'id': 'dac-batch-order'},
             {'kind': 'historical-case', 'id': 'stale-palette-view'},
             {'kind': 'historical-case', 'id': 'dropped-dac-component'},
             {'kind': 'historical-case', 'id': 'wrong-lane-mask'},
             {'kind': 'historical-case', 'id': 'stale-read-plane'}],
 'worlds_enabled': ['timing_world', 'audio_world', 'palette_world']}
