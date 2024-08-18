def validate_script(script, router):
    prompt = f"Validate the following YouTube script and return 'VALID' if it's good, or 'INVALID' with reasons if not:\n\n{script}"
    response = router.route(prompt).text.strip().upper()
    return response.startswith('VALID')
