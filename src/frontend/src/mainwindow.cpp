#include "mainwindow.h"
#include "./ui_mainwindow.h"


#include "page_networkscan.h"
#include "page_rsaencryption.h"
#include "page_hashcrack.h"
#include "test_page.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), ui(new Ui::MainWindow)
{
    // initalize the ui-elements
    ui->setupUi(this);

    ui->toolbar->addWidget(new page_hashcrack(this));
    ui->toolbar->addWidget(new page_networkscan(this));
    ui->toolbar->addWidget(new page_rsaencryption(this));
    ui->toolbar->addWidget(new test_page(this));

    // connect with logic
    // important! - the order of the pages must match the order in the navigation bar.
    connect(ui->navigationbar, &QListWidget::currentRowChanged,
            ui->toolbar, &QStackedWidget::setCurrentIndex);

    // initalize the statusbar
    ui->statusbar->showMessage("Bereit");
}

MainWindow::~MainWindow()
{
    delete ui;
}
