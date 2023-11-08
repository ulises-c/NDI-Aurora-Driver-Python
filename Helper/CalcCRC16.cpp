#include <iostream>

void CalcCRC16(int data, unsigned int* puCRC16)
{
    static int oddparity[16] = { 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0 };
    data = (data ^ (*puCRC16 & 0xff)) & 0xff;
    *puCRC16 >>= 8;
    if (oddparity[data & 0x0f] ^ oddparity[data >> 4])
    {
        *puCRC16 ^= 0xc001;
    }
    data <<= 6;
    *puCRC16 ^= data;
    data <<= 1;
    *puCRC16 ^= data;
}

int main()
{
    std::string data_str = "RESET";
    unsigned int crc16 = 0xFFFF;
    for (char ch : data_str)
    {
        CalcCRC16(static_cast<int>(ch), &crc16);
    }
    std::cout << "The CRC16 of '" << data_str << "' is " << crc16 << ".\n";
    return 0;
}
