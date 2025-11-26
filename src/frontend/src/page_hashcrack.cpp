#include "page_hashcrack.h"
#include "./ui_page_hashcrack.h"

page_hashcrack::page_hashcrack(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::page_hashcrack)
{
    ui->setupUi(this);

    // INSERT LOGIC FOR HASH CRACK PAGE HERE
}

page_hashcrack::~page_hashcrack()
{
    delete ui;
}