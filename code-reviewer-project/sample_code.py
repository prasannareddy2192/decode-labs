def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)


def get_user_discount(user):
    if user.is_premium == True:
        return 0.2
    else:
        return 0


def process_items(items):
    result = []
    for i in range(len(items)):
        if items[i] > 0:
            result.append(items[i] * 2)
    return result


average = calculate_average([])
print(average)