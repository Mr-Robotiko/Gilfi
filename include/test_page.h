#ifndef test_page_h
#define test_page_h

#include <QWidget>

QT_BEGIN_NAMESPACE
namespace Ui {
class test_page;
}
QT_END_NAMESPACE

class test_page : public QWidget
{
    Q_OBJECT

public:
    explicit test_page(QWidget *parent = nullptr);
    ~test_page();

private:
    Ui::test_page *ui;
};

#endif // test_page_h