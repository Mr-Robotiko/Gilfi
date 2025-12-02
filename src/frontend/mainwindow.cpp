#include "mainwindow.h"
#include "./ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    // initalize the ui-elements
    ui->setupUi(this);

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
