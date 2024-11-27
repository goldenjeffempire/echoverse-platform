from profanity_check import predict

def moderate_content(text):
    """
    Moderate the content of a given text for offensive language.
    Returns True if content is clean, False if content is inappropriate.
    """
    # The model returns 0 for clean content and 1 for offensive content
    is_clean = predict([text])[0]
    return is_clean == 0
