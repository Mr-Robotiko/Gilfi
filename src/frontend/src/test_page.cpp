#include "test_page.h"
#include "./ui_test_page.h" 

test_page::test_page(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::test_page)
{
    ui->setupUi(this);

    // INSERT LOGIC FOR TEST PAGE HERE
}

test_page::~test_page()
{
    delete ui;
}