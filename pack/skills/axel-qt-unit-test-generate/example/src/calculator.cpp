#include "calculator.h"

Calculator::Calculator() : m_lastResult(0)
{
}

int Calculator::add(int a, int b)
{
    return a + b;
}

int Calculator::sub(int a, int b)
{
    return a - b;
}

int Calculator::divide(int a, int b)
{
    if (b == 0) {
        return 0;
    }
    return a / b;
}

int Calculator::classify(int value)
{
    if (value > 0) {
        return 1;
    } else if (value < 0) {
        return -1;
    } else {
        return 0;
    }
}

int Calculator::compute(int a, int b, int op)
{
    int result = 0;
    switch (op) {
    case 0: // add
        result = add(a, b);
        break;
    case 1: // sub
        result = sub(a, b);
        break;
    case 2: // multiply
        result = doMultiply(a, b);
        break;
    case 3: // divide
        result = doDivide(a, b);
        break;
    default:
        result = 0;
        break;
    }
    m_lastResult = result;
    return result;
}

QString Calculator::formatResult(int value, bool withSign, bool withCommas)
{
    QString result;
    if (value < 0) {
        result = QString::number(-value);
        if (withSign) {
            result = "-" + result;
        }
    } else {
        result = QString::number(value);
        if (withSign) {
            result = "+" + result;
        }
    }

    if (withCommas && result.length() > 3) {
        // 插入千位分隔符
        QString formatted;
        int signLen = (result.startsWith('-') || result.startsWith('+')) ? 1 : 0;
        int digitCount = result.length() - signLen;
        for (int i = 0; i < result.length(); i++) {
            if (i > signLen && (digitCount - (i - signLen)) % 3 == 0) {
                formatted += ',';
            }
            formatted += result[i];
        }
        result = formatted;
    }

    return result;
}

bool Calculator::validateInput(const QString &input)
{
    if (input.isEmpty()) {
        return false;
    }

    bool allDigits = true;
    bool hasSign = false;
    for (int i = 0; i < input.length(); i++) {
        QChar c = input[i];
        if (i == 0 && (c == '-' || c == '+')) {
            hasSign = true;
            continue;
        }
        if (!c.isDigit()) {
            allDigits = false;
            break;
        }
    }

    if (!allDigits && !hasSign) {
        return false;
    }

    if (input.length() > 100) {
        return false;
    }

    return true;
}

int Calculator::parseNumber(const QString &str, bool *ok)
{
    if (ok) *ok = false;

    if (str.isEmpty()) {
        return 0;
    }

    bool negative = false;
    int start = 0;
    if (str[0] == '-') {
        negative = true;
        start = 1;
    } else if (str[0] == '+') {
        start = 1;
    }

    int result = 0;
    for (int i = start; i < str.length(); i++) {
        QChar c = str[i];
        if (!c.isDigit()) {
            return 0;
        }
        result = result * 10 + c.digitValue();
    }

    if (ok) *ok = true;
    return negative ? -result : result;
}

int Calculator::doMultiply(int a, int b)
{
    return a * b;
}

int Calculator::doDivide(int a, int b)
{
    if (b == 0) {
        return 0;
    }
    return a / b;
}
