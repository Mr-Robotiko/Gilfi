#include "page_rsaencryption.h"
#include "./ui_page_rsaencryption.h" 

page_rsaencryption::page_rsaencryption(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::page_rsaencryption)
{
    ui->setupUi(this);

    // INSERT LOGIC FOR RSA ENCRYPTION PAGE HERE
}

page_rsaencryption::~page_rsaencryption()
{
    delete ui;
}