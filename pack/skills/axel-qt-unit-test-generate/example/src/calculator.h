#ifndef CALCULATOR_H
#define CALCULATOR_H

#include <QString>

class Calculator
{
public:
    Calculator();

    // 简单函数 (P3 预期)
    int add(int a, int b);
    int sub(int a, int b);

    // 中等复杂度 (P2 预期)
    int divide(int a, int b);
    int classify(int value);

    // 高复杂度 (P1/P0 预期)
    int compute(int a, int b, int op);
    QString formatResult(int value, bool withSign, bool withCommas);

    // 安全敏感 (P0 预期)
    bool validateInput(const QString &input);

    // 数据处理
    int parseNumber(const QString &str, bool *ok = nullptr);

private:
    int m_lastResult;

    int doMultiply(int a, int b);
    int doDivide(int a, int b);
};

#endif // CALCULATOR_H
