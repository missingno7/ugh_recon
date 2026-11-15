"""Remaining5R provider ownership and full-window scratch composition."""
SPEC = {'component':'resource_world',
 'legacy':'world_cases.resource_data_operators',
 'api':{'sprites':{'suites':['render','render_primitives'],'filter':True,'expected_cases':94,'allowed_rejections':[]},
        'resources':{'suites':['demo_scripts','scene','ice','dos_input','game_services'],'filter':True,'expected_cases':250,'allowed_rejections':[]}},
 'defects':[{'kind':'historical-case','id':'lost-shared-animation-word'},
            {'kind':'historical-case','id':'missed-serialization'},
            {'kind':'historical-case','id':'clipped-workspace'},
            {'kind':'historical-case','id':'wrong-view-token'},
            {'kind':'historical-case','id':'stale-parent-tail-overwrite'}],
 'worlds_enabled':['timing_world','audio_world','palette_world','input_world','video_pages','pixel_world','presentation_world','run_world','random_world','player_world','resource_catalog','platform_world','actor_world','enemy_world','item_world','front_end_world','lifecycle_world','resource_world','object_identities']}
