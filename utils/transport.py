def transport_options(distance):

    if distance < 300:
        return """
- Bus: ₹500 – ₹1,200
- Train: ₹600 – ₹1,500
"""

    elif distance < 1000:
        return """
- Train: ₹1,200 – ₹2,500
- Flight: ₹3,500 – ₹6,000
"""

    else:
        return """
- Train: ₹2,000 – ₹4,000
- Flight: ₹4,500 – ₹8,000
"""
