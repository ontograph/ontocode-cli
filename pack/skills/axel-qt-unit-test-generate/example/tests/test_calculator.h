#ifndef TEST_CALCULATOR_H
#define TEST_CALCULATOR_H

#include <QtTest/QtTest>
#include "calculator.h"

class TestCalculator : public QObject
{
    Q_OBJECT

private slots:
    void initTestCase();
    void cleanupTestCase();
    void init();
    void cleanup();
    void testAdd_smoke();
    void testAdd_data();
    void testAdd();
    void testSub_smoke();
    void testSub_data();
    void testSub();
    void testDoDivide_smoke();
    void testDoMultiply_smoke();
    void testCompute_smoke();
    void testCompute_data();
    void testCompute();
    void testFormatResult_smoke();
    void testFormatResult_data();
    void testFormatResult();
    void testValidateInput_smoke();
    void testValidateInput_data();
    void testValidateInput();
    void testValidateInput_path1();
    void testValidateInput_path2();
    void testValidateInput_signal();
    void testValidateInput_interaction();
    void testValidateInput_nullInput();
    void testValidateInput_overflow();
    void testParseNumber_smoke();
    void testParseNumber_path1();
    void testParseNumber_path2();
    void testParseNumber_signal();
    void testParseNumber_interaction();
    void testParseNumber_nullInput();
    void testParseNumber_overflow();
    void testClassify_smoke();
    void testDivide_smoke();
    void testCalculator_smoke();
};

#endif // TEST_CALCULATOR_H
