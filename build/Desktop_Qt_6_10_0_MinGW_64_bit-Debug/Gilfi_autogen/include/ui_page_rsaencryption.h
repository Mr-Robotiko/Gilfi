/********************************************************************************
** Form generated from reading UI file 'page_rsaencryption.ui'
**
** Created by: Qt User Interface Compiler version 6.10.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_PAGE_RSAENCRYPTION_H
#define UI_PAGE_RSAENCRYPTION_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QTextEdit>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_page_rsaencryption
{
public:
    QVBoxLayout *verticalLayout_5;
    QVBoxLayout *verticalLayout_3;
    QGridLayout *gridLayout_3;
    QPushButton *pushButton_r_start;
    QLabel *label_5;
    QLabel *label_6;
    QLineEdit *lineEdit_r_inputtext;
    QLineEdit *lineEdit_r_key;
    QTextEdit *textEdit_r_output;

    void setupUi(QWidget *page_rsaencryption)
    {
        if (page_rsaencryption->objectName().isEmpty())
            page_rsaencryption->setObjectName("page_rsaencryption");
        page_rsaencryption->resize(400, 300);
        page_rsaencryption->setMinimumSize(QSize(0, 0));
        page_rsaencryption->setMaximumSize(QSize(16777215, 16777215));
        verticalLayout_5 = new QVBoxLayout(page_rsaencryption);
        verticalLayout_5->setObjectName("verticalLayout_5");
        verticalLayout_3 = new QVBoxLayout();
        verticalLayout_3->setObjectName("verticalLayout_3");
        gridLayout_3 = new QGridLayout();
        gridLayout_3->setObjectName("gridLayout_3");
        pushButton_r_start = new QPushButton(page_rsaencryption);
        pushButton_r_start->setObjectName("pushButton_r_start");

        gridLayout_3->addWidget(pushButton_r_start, 4, 2, 1, 1);

        label_5 = new QLabel(page_rsaencryption);
        label_5->setObjectName("label_5");

        gridLayout_3->addWidget(label_5, 3, 0, 1, 1);

        label_6 = new QLabel(page_rsaencryption);
        label_6->setObjectName("label_6");

        gridLayout_3->addWidget(label_6, 2, 0, 1, 1);

        lineEdit_r_inputtext = new QLineEdit(page_rsaencryption);
        lineEdit_r_inputtext->setObjectName("lineEdit_r_inputtext");

        gridLayout_3->addWidget(lineEdit_r_inputtext, 2, 1, 1, 1);

        lineEdit_r_key = new QLineEdit(page_rsaencryption);
        lineEdit_r_key->setObjectName("lineEdit_r_key");

        gridLayout_3->addWidget(lineEdit_r_key, 3, 1, 1, 1);


        verticalLayout_3->addLayout(gridLayout_3);

        textEdit_r_output = new QTextEdit(page_rsaencryption);
        textEdit_r_output->setObjectName("textEdit_r_output");

        verticalLayout_3->addWidget(textEdit_r_output);


        verticalLayout_5->addLayout(verticalLayout_3);


        retranslateUi(page_rsaencryption);

        QMetaObject::connectSlotsByName(page_rsaencryption);
    } // setupUi

    void retranslateUi(QWidget *page_rsaencryption)
    {
        page_rsaencryption->setWindowTitle(QCoreApplication::translate("page_rsaencryption", "RSA Encryption", nullptr));
        pushButton_r_start->setText(QCoreApplication::translate("page_rsaencryption", "Start Encryption", nullptr));
        label_5->setText(QCoreApplication::translate("page_rsaencryption", "Input key", nullptr));
        label_6->setText(QCoreApplication::translate("page_rsaencryption", "Input text", nullptr));
    } // retranslateUi

};

namespace Ui {
    class page_rsaencryption: public Ui_page_rsaencryption {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PAGE_RSAENCRYPTION_H
