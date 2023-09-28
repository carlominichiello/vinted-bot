def get_feedback_out_of_5(user):
    return round(user['feedback_reputation'] * 5, 2)
