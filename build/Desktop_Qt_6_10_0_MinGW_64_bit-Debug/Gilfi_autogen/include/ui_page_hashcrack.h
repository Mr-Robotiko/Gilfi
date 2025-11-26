/********************************************************************************
** Form generated from reading UI file 'page_hashcrack.ui'
**
** Created by: Qt User Interface Compiler version 6.10.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_PAGE_HASHCRACK_H
#define UI_PAGE_HASHCRACK_H

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

class Ui_page_hashcrack
{
public:
    QVBoxLayout *verticalLayout_4;
    QVBoxLayout *verticalLayout;
    QGridLayout *gridLayout;
    QLabel *label;
    QPushButton *pushButton_h_start;
    QLineEdit *lineEdit_h_hash;
    QLabel *label_2;
    QLineEdit *lineEdit_h_hashformat;
    QTextEdit *textEdit_h_output;

    void setupUi(QWidget *page_hashcrack)
    {
        if (page_hashcrack->objectName().isEmpty())
            page_hashcrack->setObjectName("page_hashcrack");
        page_hashcrack->resize(400, 300);
        verticalLayout_4 = new QVBoxLayout(page_hashcrack);
        verticalLayout_4->setObjectName("verticalLayout_4");
        verticalLayout = new QVBoxLayout();
        verticalLayout->setObjectName("verticalLayout");
        gridLayout = new QGridLayout();
        gridLayout->setObjectName("gridLayout");
        label = new QLabel(page_hashcrack);
        label->setObjectName("label");

        gridLayout->addWidget(label, 2, 0, 1, 1);

        pushButton_h_start = new QPushButton(page_hashcrack);
        pushButton_h_start->setObjectName("pushButton_h_start");

        gridLayout->addWidget(pushButton_h_start, 4, 2, 1, 1);

        lineEdit_h_hash = new QLineEdit(page_hashcrack);
        lineEdit_h_hash->setObjectName("lineEdit_h_hash");

        gridLayout->addWidget(lineEdit_h_hash, 2, 1, 1, 1);

        label_2 = new QLabel(page_hashcrack);
        label_2->setObjectName("label_2");

        gridLayout->addWidget(label_2, 3, 0, 1, 1);

        lineEdit_h_hashformat = new QLineEdit(page_hashcrack);
        lineEdit_h_hashformat->setObjectName("lineEdit_h_hashformat");

        gridLayout->addWidget(lineEdit_h_hashformat, 3, 1, 1, 1);


        verticalLayout->addLayout(gridLayout);

        textEdit_h_output = new QTextEdit(page_hashcrack);
        textEdit_h_output->setObjectName("textEdit_h_output");

        verticalLayout->addWidget(textEdit_h_output);


        verticalLayout_4->addLayout(verticalLayout);


        retranslateUi(page_hashcrack);

        QMetaObject::connectSlotsByName(page_hashcrack);
    } // setupUi

    void retranslateUi(QWidget *page_hashcrack)
    {
        page_hashcrack->setWindowTitle(QCoreApplication::translate("page_hashcrack", "Hash Cracker", nullptr));
        label->setText(QCoreApplication::translate("page_hashcrack", "Hash", nullptr));
        pushButton_h_start->setText(QCoreApplication::translate("page_hashcrack", "Start Crack", nullptr));
        label_2->setText(QCoreApplication::translate("page_hashcrack", "Hash-format", nullptr));
    } // retranslateUi

};

namespace Ui {
    class page_hashcrack: public Ui_page_hashcrack {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PAGE_HASHCRACK_H
