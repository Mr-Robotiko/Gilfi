/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 6.10.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QListWidget>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStackedWidget>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralwidget;
    QHBoxLayout *horizontalLayout;
    QListWidget *navigationbar;
    QStackedWidget *toolbar;
    QMenuBar *menubar;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName("MainWindow");
        MainWindow->resize(800, 600);
        MainWindow->setStyleSheet(QString::fromUtf8("QLineEdit {\n"
"    padding: 5px;\n"
"    border: 1px solid #b0b0b0;\n"
"    border-radius: 4px;\n"
"    background-color: #f7f7f7; \n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: #007bff; \n"
"    color: white;\n"
"    border: none;\n"
"    padding: 8px 15px;\n"
"    border-radius: 4px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #0056b3;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #004085;\n"
"}\n"
"\n"
"#textEdit_h_output, #textEdit_n_output, #textEdit_r_output {\n"
"    background-color: #333333; \n"
"    color: #00ff7f; \n"
"    font-family: monospace;\n"
"    border: 1px solid #666666;\n"
"    border-radius: 4px;\n"
"    padding: 10px;\n"
"}\n"
"\n"
"QLabel {\n"
"   color: black;\n"
"}"));
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName("centralwidget");
        horizontalLayout = new QHBoxLayout(centralwidget);
        horizontalLayout->setObjectName("horizontalLayout");
        navigationbar = new QListWidget(centralwidget);
        new QListWidgetItem(navigationbar);
        new QListWidgetItem(navigationbar);
        new QListWidgetItem(navigationbar);
        navigationbar->setObjectName("navigationbar");
        navigationbar->setStyleSheet(QString::fromUtf8("#navigationbar {\n"
"    background-color: #f0f0f0;\n"
"    border: none;\n"
"    padding: 10px 5px; \n"
"    outline: 0; \n"
"}\n"
"\n"
"#navigationbar::item {\n"
"    padding: 10px 15px; \n"
"    margin-bottom: 8px;\n"
"    \n"
"    background-color: white;\n"
"    color: #333333; \n"
"    border: 1px solid #d0d0d0;\n"
"    border-radius: 4px; \n"
"}\n"
"\n"
"#navigationbar::item:hover {\n"
"    background-color: #e6f7ff;\n"
"    border: 1px solid #99d8ff;\n"
"}\n"
"\n"
"#navigationbar::item:selected {\n"
"    background-color: #007bff; \n"
"    color: white; \n"
"    border: 1px solid #0056b3; \n"
"    font-weight: bold;\n"
"}"));

        horizontalLayout->addWidget(navigationbar, 0, Qt::AlignmentFlag::AlignLeft);

        toolbar = new QStackedWidget(centralwidget);
        toolbar->setObjectName("toolbar");
        toolbar->setStyleSheet(QString::fromUtf8("#toolbar {\n"
"    background-color: white;\n"
"    border: 1px solid #d0d0d0; \n"
"    border-radius: 6px; \n"
"    padding: 10px; \n"
"}"));

        horizontalLayout->addWidget(toolbar);

        MainWindow->setCentralWidget(centralwidget);
        menubar = new QMenuBar(MainWindow);
        menubar->setObjectName("menubar");
        menubar->setGeometry(QRect(0, 0, 800, 21));
        MainWindow->setMenuBar(menubar);
        statusbar = new QStatusBar(MainWindow);
        statusbar->setObjectName("statusbar");
        MainWindow->setStatusBar(statusbar);

        retranslateUi(MainWindow);

        toolbar->setCurrentIndex(0);


        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QCoreApplication::translate("MainWindow", "MainWindow", nullptr));

        const bool __sortingEnabled = navigationbar->isSortingEnabled();
        navigationbar->setSortingEnabled(false);
        QListWidgetItem *___qlistwidgetitem = navigationbar->item(0);
        ___qlistwidgetitem->setText(QCoreApplication::translate("MainWindow", "Hash Cracker", nullptr));
        QListWidgetItem *___qlistwidgetitem1 = navigationbar->item(1);
        ___qlistwidgetitem1->setText(QCoreApplication::translate("MainWindow", "Network Scanner", nullptr));
        QListWidgetItem *___qlistwidgetitem2 = navigationbar->item(2);
        ___qlistwidgetitem2->setText(QCoreApplication::translate("MainWindow", "RSA Encryption", nullptr));
        navigationbar->setSortingEnabled(__sortingEnabled);

    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
