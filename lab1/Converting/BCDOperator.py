from Utils.ArrayStringConverter import ArrayStringConverter


class BCDOperator:
    def __init__(self, bits = 32):
        self.bits = bits
        self.converter = ArrayStringConverter()

    def decimal_to_bcd_8421(self, num):
        """8421 BCD код"""
        arr = [0] * self.bits
        negative = num < 0
        num = abs(num)
        digits = []
        if num == 0:
            digits = [0]
        else:
            while num > 0:
                digits.append(num % 10)
                num //= 10
        idx = self.bits - 1
        for d in digits:
            for i in range(3, -1, -1):
                if idx >= 0:
                    arr[idx] = d % 2
                    d //= 2
                    idx -= 1

        if negative:
            arr[0] = 1
        return arr

    def bcd_8421_to_decimal(self, arr):

        sign = -1 if arr[0] == 1 else 1
        result = 0
        power = 1
        for i in range(self.bits - 1, -1, -4):
            if i < 3:
                break
            digit = 0
            for j in range(4):
                if i - j >= 0:
                    digit += arr[i - j] * (2 ** j)
            if digit < 10:
                result += digit * power
                power *= 10
        return sign * result

    def display_bcd(self, num):
        
        print("\n=== BCD 8421 ===")
        print(f"Число: {num}")
        arr = self.decimal_to_bcd_8421(num)
        dec = self.bcd_8421_to_decimal(arr)

        print(f"BCD код: {self.converter.array_to_string(arr)}")
        print(f"Проверка (dec): {dec}")

        return arr