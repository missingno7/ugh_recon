"""World-specific inputs/operators; common stages live in world_gate."""
SPEC = {'component': 'video_pages',
 'legacy': 'world_cases.legacy_video_pages',
 'api': {'api': {'suites': ['video', 'video_upload', 'render_primitives', 'render'],
                 'filter': False,
                 'expected_cases': 1118,
                 'allowed_rejections': []}},
 'defects': [{'kind': 'historical-case', 'id': 'wrong-lane-mask'},
             {'kind': 'historical-case', 'id': 'stale-read-plane'},
             {'kind': 'historical-case', 'id': 'frame-start-copy-snapshot'},
             {'kind': 'historical-case', 'id': 'clipped-destination'},
             {'kind': 'historical-case', 'id': 'reordered-retrace-page-swap'},
             {'kind': 'historical-case', 'id': 'missed-serialization'}],
 'worlds_enabled': ['timing_world', 'audio_world', 'palette_world', 'input_world', 'video_pages']}
