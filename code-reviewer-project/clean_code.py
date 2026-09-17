def calculate_average(numbers):
    if not numbers:
        raise ValueError("Cannot calculate average of an empty list")
    return sum(numbers) / len(numbers)


def get_user_discount(user):
    return 0.2 if user.is_premium else 0