#ifndef page_hashcrack_h
#define page_hashcrack_h

#include <QWidget>

QT_BEGIN_NAMESPACE
namespace Ui {
class page_hashcrack;
}
QT_END_NAMESPACE

class page_hashcrack : public QWidget
{
    Q_OBJECT

public:
    explicit page_hashcrack(QWidget *parent = nullptr);
    ~page_hashcrack();

private:
    Ui::page_hashcrack *ui;
};

#endif // page_hashcrack_h