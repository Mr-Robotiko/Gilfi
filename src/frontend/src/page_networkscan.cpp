#include "page_networkscan.h"
#include "./ui_page_networkscan.h" 

page_networkscan::page_networkscan(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::page_networkscan)
{
    ui->setupUi(this);

    // INSERT LOGIC FOR NETWORK SCAN PAGE HERE
}

page_networkscan::~page_networkscan()
{
    delete ui;
}