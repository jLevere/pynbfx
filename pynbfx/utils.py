def letter_in_range(value: int, letter_range: range) -> str:
    """
    Converts a numeric value within a range to its matching
    letter in the alphabet. The letter is determined based on its
    position within the range.

    Args:
        value (int): The numeric value to convert, expected to be within the given range.
        letter_range (range): The range representing letter positions, e.g., range(0, 26) for 'A' to 'Z'.

    Returns:
        str: The corresponding letter in the alphabet.

    Raises:
        ValueError: If the value is outside the provided range.
    """
    if value not in letter_range:
        raise ValueError(f"Value {value} is out of the specified range.")

    return chr(ord("a") + (value - letter_range.start))