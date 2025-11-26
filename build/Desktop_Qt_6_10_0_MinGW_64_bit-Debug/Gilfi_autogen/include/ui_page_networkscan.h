/********************************************************************************
** Form generated from reading UI file 'page_networkscan.ui'
**
** Created by: Qt User Interface Compiler version 6.10.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_PAGE_NETWORKSCAN_H
#define UI_PAGE_NETWORKSCAN_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QTextEdit>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_page_networkscan
{
public:
    QHBoxLayout *horizontalLayout_2;
    QVBoxLayout *verticalLayout_2;
    QGridLayout *gridLayout_2;
    QLineEdit *lineEdit_n_ip;
    QLabel *label_3;
    QLineEdit *lineEdit_n_ports;
    QLabel *label_4;
    QPushButton *pushButton_n_start;
    QTextEdit *textEdit_n_output;

    void setupUi(QWidget *page_networkscan)
    {
        if (page_networkscan->objectName().isEmpty())
            page_networkscan->setObjectName("page_networkscan");
        page_networkscan->resize(400, 300);
        horizontalLayout_2 = new QHBoxLayout(page_networkscan);
        horizontalLayout_2->setObjectName("horizontalLayout_2");
        verticalLayout_2 = new QVBoxLayout();
        verticalLayout_2->setObjectName("verticalLayout_2");
        gridLayout_2 = new QGridLayout();
        gridLayout_2->setObjectName("gridLayout_2");
        lineEdit_n_ip = new QLineEdit(page_networkscan);
        lineEdit_n_ip->setObjectName("lineEdit_n_ip");

        gridLayout_2->addWidget(lineEdit_n_ip, 2, 1, 1, 1);

        label_3 = new QLabel(page_networkscan);
        label_3->setObjectName("label_3");

        gridLayout_2->addWidget(label_3, 3, 0, 1, 1);

        lineEdit_n_ports = new QLineEdit(page_networkscan);
        lineEdit_n_ports->setObjectName("lineEdit_n_ports");

        gridLayout_2->addWidget(lineEdit_n_ports, 3, 1, 1, 1);

        label_4 = new QLabel(page_networkscan);
        label_4->setObjectName("label_4");

        gridLayout_2->addWidget(label_4, 2, 0, 1, 1);

        pushButton_n_start = new QPushButton(page_networkscan);
        pushButton_n_start->setObjectName("pushButton_n_start");

        gridLayout_2->addWidget(pushButton_n_start, 4, 2, 1, 1);


        verticalLayout_2->addLayout(gridLayout_2);

        textEdit_n_output = new QTextEdit(page_networkscan);
        textEdit_n_output->setObjectName("textEdit_n_output");

        verticalLayout_2->addWidget(textEdit_n_output);


        horizontalLayout_2->addLayout(verticalLayout_2);


        retranslateUi(page_networkscan);

        QMetaObject::connectSlotsByName(page_networkscan);
    } // setupUi

    void retranslateUi(QWidget *page_networkscan)
    {
        page_networkscan->setWindowTitle(QCoreApplication::translate("page_networkscan", "Network Scanner", nullptr));
        label_3->setText(QCoreApplication::translate("page_networkscan", "Ports", nullptr));
        label_4->setText(QCoreApplication::translate("page_networkscan", "Target/Host-IP", nullptr));
        pushButton_n_start->setText(QCoreApplication::translate("page_networkscan", "Start Scan", nullptr));
    } // retranslateUi

};

namespace Ui {
    class page_networkscan: public Ui_page_networkscan {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PAGE_NETWORKSCAN_H
