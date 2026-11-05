sample_payload = {
    'model': {'id': 'gemini-3.8-flash', 'display_name': 'Gemini 3.8 Flash (High)'},
    'quota': {
        'gemini-5h': {'remaining_fraction': 0.45, 'reset_time': '2026-07-04T14:45:00Z'},
        'gemini-weekly': {'remaining_fraction': 0.72, 'reset_time': '2026-07-11T04:00:00Z'},
        '3p-5h': {'remaining_fraction': 0.85, 'reset_time': '2026-07-04T12:40:00Z'},
        '3p-weekly': {'remaining_fraction': 0.90, 'reset_time': '2026-07-11T12:57:00Z'}
    }
}

# Test 1: Gemini active
model_str = f"{sample_payload['model']['id']} {sample_payload['model']['display_name']}".lower()
is_claude = any(k in model_str for k in ('claude', 'anthropic', 'sonnet', 'opus', 'haiku', '3p'))
print('Model:', sample_payload['model']['display_name'], '-> Is Claude pool?', is_claude)

# Test 2: Claude active
sample_payload['model'] = {'id': 'claude-3-7-sonnet', 'display_name': 'Claude Sonnet 3.7 (Thinking)'}
model_str = f"{sample_payload['model']['id']} {sample_payload['model']['display_name']}".lower()
is_claude = any(k in model_str for k in ('claude', 'anthropic', 'sonnet', 'opus', 'haiku', '3p'))
print('Model:', sample_payload['model']['display_name'], '-> Is Claude pool?', is_claude)

# Test 3: Opus with only 'display_name'
sample_payload['model'] = {'display_name': 'Claude Opus 4.6'}
model_str = f"{sample_payload['model'].get('id', '')} {sample_payload['model']['display_name']}".lower()
is_claude = any(k in model_str for k in ('claude', 'anthropic', 'sonnet', 'opus', 'haiku', '3p'))
print('Model:', sample_payload['model']['display_name'], '-> Is Claude pool?', is_claude)
